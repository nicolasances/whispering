
from datetime import datetime
from fastapi import Request
from totoms.TotoDelegateDecorator import toto_delegate
from totoms.model.UserContext import UserContext
from totoms.model.ExecutionContext import ExecutionContext
import os
import shutil
from whispercpp import Whisper
from storage import delete_audio_file_from_s3, download_audio_file_from_s3, list_audio_files_to_process, store_audio_file_on_s3, store_transcription_on_s3

w = Whisper('medium')

# Get upload directory from environment variable
UPLOAD_DIR = os.getenv('AUDIO_UPLOAD_DIR', '/app/audiofiles')

@toto_delegate
async def transcribe_recording(request: Request, user_context: UserContext, exec_context: ExecutionContext):
    
    form = await request.form()
    file = form['file']

    if file: 
        filename = file.filename
        fileobj = file.file
        
        upload_name = os.path.join(UPLOAD_DIR, filename)
        with open(upload_name, 'wb') as upload_file:
            shutil.copyfileobj(fileobj, upload_file)
        
        try:
            result = w.transcribe(upload_name)
            text = w.extract_text(result)
            
            # test is an array of strings that need to be joined
            full_text = "".join(text)
            
            return {"text": full_text}
        
        finally:
            # Clean up the audio file
            if os.path.exists(upload_name):
                os.unlink(upload_name)
    
    return {"error": "No file uploaded"}

@toto_delegate
async def start_transcription_job(request: Request, user_context: UserContext, exec_context: ExecutionContext):
    '''
    This delegate handles transcription requests, but ASYNCHRONOUSLY: it starts a job 
    - it uploads the audio file to S3 
    - it starts a transcription job (this same container in job mode)
    - it returns a job ID to the user
    '''
    
    form = await request.form()
    file = form['file']

    if file: 
        filename = file.filename
        fileobj = file.file
        
        local_file_path = os.path.join(UPLOAD_DIR, filename)
        with open(local_file_path, 'wb') as upload_file:
            shutil.copyfileobj(fileobj, upload_file)
            
        try:
            # Generate a unique file ID using timestamp in milliseconds
            file_id = str(int(datetime.now().timestamp() * 1000))
            
            # Upload to S3
            s3_filepath = store_audio_file_on_s3(local_file_path, file_id)
            
            exec_context.logger.log(exec_context.cid, f"Uploaded audio file to S3 at {s3_filepath}")
            
            # Start the ECS job using the boto SDK
            import boto3
            
            # Get AWS region from environment
            aws_region = os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION', 'eu-north-1'))
            ecs_client = boto3.client('ecs', region_name=aws_region)
            environment = os.getenv('ENVIRONMENT', 'dev')
            cluster_arn = os.getenv('ECS_CLUSTER_ARN', f'toto-ecs-{environment}')
            subnets = os.getenv('ECS_SUBNETS', '').split(',')
            security_group = os.getenv('ECS_SECURITY_GROUP', '')
            
            exec_context.logger.log(exec_context.cid, f"Running task on cluster {cluster_arn} in subnets {subnets} with security group {security_group} in region {aws_region} - Environment: {environment}")
            
            response = ecs_client.run_task(
                cluster=cluster_arn,
                taskDefinition=f'whispering-{environment}-job',
                launchType='FARGATE',
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': subnets,
                        'securityGroups': [security_group],
                        'assignPublicIp': 'ENABLED'
                    }
                }
            )
            
            exec_context.logger.log(exec_context.cid, f"Started ECS job task: {response['tasks'][0]['taskArn']}")
            
            # Return the job ID to the user
            return {"jobId": file_id, "taskArn": response['tasks'][0]['taskArn']}
        
        finally:
            # Clean up the audio file
            if os.path.exists(local_file_path):
                os.unlink(local_file_path)
    
    return {"error": "No file uploaded"}

    

def run_as_job():
    '''
    Runs this service as a job
    
    To run as a job, it expects the following environment variables to be set:
    - WHISPERING_S3_BUCKET_NAME: Name of the S3 bucket to store the transcription (should be set as part of the task definition on ECS)
    
    This basically processes all the audio files found in the S3 bucket and deletes them once processed.
    The transcriptions are stored back on S3. 
    Note that the file name is a uuid and the transcription will have the same name with a -transcription suffix
    '''
    
    # List audio files from S3
    audio_files = list_audio_files_to_process()
    
    print(f"Found {len(audio_files)} audio files to process")
    
    # Process each audio file
    for s3_key in audio_files:
        
        print(f"Processing audio file: {s3_key}")
        
        # Download the audio file locally
        local_file_path = os.path.join(UPLOAD_DIR, os.path.basename(s3_key))
        
        download_audio_file_from_s3(s3_key, local_file_path)
        
        try:
            # Transcribe the audio file
            result = w.transcribe(local_file_path)
            text = w.extract_text(result)
            
            # Join the text array into a single string
            full_text = "".join(text)
            
            print(f"Transcription completed successfully")
            print(f"Transcription:\n{full_text}")
            
            # Store the transcription on S3
            store_transcription_on_s3(full_text, os.path.basename(s3_key))
            
            print(f"Text stored on S3: {s3_key}")
            
            # Delete the audio file from S3
            delete_audio_file_from_s3(s3_key)
            
            print(f"Deleted audio file from S3: {s3_key}")
    
        except Exception as e:
            print(f"Error during transcription: {e}")
    