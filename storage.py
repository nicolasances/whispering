
import os
import boto3
from datetime import datetime


def store_text_on_s3(text: str, original_filename: str = None) -> str:
    """
    Store transcription text on S3
    
    Args:
        text: The transcription text to store
        original_filename: Optional original audio filename for reference
    
    Returns:
        The S3 key of the stored file
    """
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is not set")
    
    base_name = os.path.splitext(original_filename)[0]
    s3_key = f"transcriptions/{base_name}.txt"
    
    # Upload to S3
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=text.encode('utf-8'),
        ContentType='text/plain'
    )
    
    return s3_key
