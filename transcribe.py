
from fastapi import Request
from totoms.TotoDelegateDecorator import toto_delegate
from totoms.model.UserContext import UserContext
from totoms.model.ExecutionContext import ExecutionContext
import os
import shutil
from whispercpp import Whisper

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