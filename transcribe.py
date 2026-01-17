
from fastapi import Request
from totoms.TotoDelegateDecorator import toto_delegate
from totoms.model.UserContext import UserContext
from totoms.model.ExecutionContext import ExecutionContext
import os
import shutil
from whispercpp import Whisper
from storage import store_text_on_s3

w = Whisper('tiny')

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
            
            return {"transcription": text}
        
        finally:
            # Clean up the audio file
            if os.path.exists(upload_name):
                os.unlink(upload_name)
    
    return {"error": "No file uploaded"}

def run_as_job():
    '''
    Runs this service as a job
    
    To run as a job, it expects the following environment variables to be set:
    - AUDIO_FILE_PATH: Path to the audio file to transcribe
    - S3_BUCKET_NAME: Name of the S3 bucket to store the transcription (should be set as part of the task definition on ECS)
    '''
    audio_file_path = os.getenv('AUDIO_FILE_PATH')
    
    if not audio_file_path or not os.path.exists(audio_file_path):
        print("AUDIO_FILE_PATH environment variable is not set or file does not exist.")
        return
    
    try:
        result = w.transcribe(audio_file_path)
        text = w.extract_text(result)
        
        # Store the text on S3
        filename = os.path.basename(audio_file_path)
        s3_key = store_text_on_s3(text, filename)
        
        print(f"Transcription completed successfully")
        print(f"Text stored on S3: {s3_key}")
        print(f"Transcription:\n{text}")
        
    except Exception as e:
        print(f"Error during transcription: {e}")
    