
import os
from totoms import (APIConfiguration, TotoEnvironment, TotoMicroserviceConfiguration, TotoMicroservice)
from totoms.TotoMicroservice import APIEndpoint, determine_environment
from config import WhisperConfig
from transcribe import run_as_job, start_transcription_job, transcribe_recording

def get_microservice_config() -> TotoMicroserviceConfiguration:
    return TotoMicroserviceConfiguration(
        service_name="whisper", 
        base_path="/whispering",
        environment=TotoEnvironment(
            hyperscaler=os.getenv("HYPERSCALER", "aws").lower(),
            hyperscaler_configuration=determine_environment()
        ), 
        custom_config=WhisperConfig, 
        api_configuration=APIConfiguration(
            api_endpoints=[
                APIEndpoint(path="/transcribe", method="POST", delegate=transcribe_recording), 
                APIEndpoint(path="/transcribejob", method="POST", delegate=start_transcription_job), 
            ]
        )
    )
    
async def start_microservice(): 
    microservice = await TotoMicroservice.init(get_microservice_config())
    port = 8080
    await microservice.start(port=port)
        
    
if __name__ == "__main__":
    import asyncio
    import sys
    
    # Check the mode
    # This service supports the "API" mode and the "job" mode
    mode = os.environ.get('MODE', 'api')
    
    if mode == 'api':
        asyncio.run(start_microservice())
    else: 
        # Run as a job
        try:
            run_as_job()
            sys.exit(0)  # Explicit success exit
        except Exception as e:
            print(f"Job failed with error: {e}")
            sys.exit(1)  # Exit with error code