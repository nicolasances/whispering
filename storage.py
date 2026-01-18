
import os
import boto3
from datetime import datetime

S3_AUDIO_FOLDER = "audio_uploads"
S3_TRANSCRIPTIONS_FOLDER = "transcriptions"
BUCKET_NAME = os.getenv('WHISPERING_S3_BUCKET_NAME')

def store_audio_file_on_s3(local_file_path: str, file_id: str) -> str:
    """
    Store audio file on S3
    
    Args:
        local_file_path: Local path to the audio file to store. This is the path on the local filesystem.
    
    Returns:
        The S3 key of the stored file
    """
    if not BUCKET_NAME:
        raise ValueError("WHISPERING_S3_BUCKET_NAME environment variable is not set")
    
    s3_filepath = f"{S3_AUDIO_FOLDER}/{file_id}"
    
    # Upload to S3
    s3_client = boto3.client('s3')
    s3_client.upload_file(local_file_path, BUCKET_NAME, s3_filepath)
    
    return s3_filepath

def list_audio_files_to_process() -> list:
    """
    List audio files to process from S3
    
    Returns:
        A list of S3 keys for audio files to process
    """
    if not BUCKET_NAME:
        raise ValueError("WHISPERING_S3_BUCKET_NAME environment variable is not set")
    
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"{S3_AUDIO_FOLDER}/")
    
    audio_files = []
    for item in response.get('Contents', []):
        audio_files.append(item['Key'])
    
    return audio_files

def download_audio_file_from_s3(s3_key: str, local_file_path: str):
    """
    Download audio file from S3 to local path
    
    Args:
        s3_key: The S3 key of the audio file to download
        local_file_path: The local path where to save the downloaded file
    """
    if not BUCKET_NAME:
        raise ValueError("WHISPERING_S3_BUCKET_NAME environment variable is not set")
    
    s3_client = boto3.client('s3')
    s3_client.download_file(BUCKET_NAME, s3_key, local_file_path)

def store_transcription_on_s3(text: str, file_id: str) -> str:
    """
    Store transcription text on S3
    
    Args:
        text: The transcription text to store
        original_filename: Optional original audio filename for reference
    
    Returns:
        The S3 key of the stored file
    """
    if not BUCKET_NAME:
        raise ValueError("WHISPERING_S3_BUCKET_NAME environment variable is not set")
    
    s3_key = f"{S3_TRANSCRIPTIONS_FOLDER}/{file_id}-transcription"
    
    # Upload to S3
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=text.encode('utf-8'),
        ContentType='text/plain'
    )
    
    return s3_key

def delete_audio_file_from_s3(s3_key: str):
    """
    Delete audio file from S3 after processing
    
    Args:
        s3_key: The S3 key of the audio file to delete
    """
    if not BUCKET_NAME:
        raise ValueError("WHISPERING_S3_BUCKET_NAME environment variable is not set")
    
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)