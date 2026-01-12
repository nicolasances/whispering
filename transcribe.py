
from fastapi import Request
from totoms.TotoDelegateDecorator import toto_delegate
from totoms.model.UserContext import UserContext
from totoms.model.ExecutionContext import ExecutionContext
import os
import shutil
from whispercpp import Whisper

w = Whisper('tiny')

UPLOAD_DIR="/workspaces/whispering/audiofiles"

@toto_delegate
async def transcribe_recording(request: Request, user_context: UserContext, exec_context: ExecutionContext):
    
    form = await request.form()
    file = form['file']

    if file: 
        filename = file.filename
        fileobj = file.file
        upload_name = os.path.join(UPLOAD_DIR, filename)
        upload_file = open(upload_name, 'wb+')
        shutil.copyfileobj(fileobj, upload_file)
        upload_file.close()
        
        result = w.transcribe(upload_name)
        text = w.extract_text(result)
        
        return {"transcription": text}
    
    return {"error": "No file uploaded"}