
from fastapi import Request
from totoms.TotoDelegateDecorator import toto_delegate
from totoms.model import ExecutionContext, UserContext

from storage import get_transcription_file_content


@toto_delegate
async def get_transcription(request: Request, user_context: UserContext, exec_context: ExecutionContext):
    '''
    A simple delegate to get the status of the transcription of an audio file. 
    
    Transcriptions are stored on S3 with the same key as the audio file. 
    This delegate looks for the transcription file on S3 and returns its content if found. If not found, it returns a "not-ready" status. 
    '''
    # 1. Get job ID from request (path parameter)
    job_id = request.path_params.get('job_id')
    
    exec_context.logger.log(exec_context.cid, f"Getting transcription for job ID: {job_id}")
    
    # 2. Look for the transcription file on S3
    transcription = get_transcription_file_content(job_id)
    
    if transcription is not None:
        return {
            "status": "completed", 
            "text": transcription
        }
    
    return {"status": "not-ready"}