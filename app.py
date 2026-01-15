
import os
from totoms import (APIConfiguration, TotoEnvironment, TotoMicroserviceConfiguration, TotoMicroservice)
from totoms.TotoMicroservice import APIEndpoint, determine_environment
from config import WhisperConfig
from transcribe import transcribe_recording

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
                APIEndpoint(path="/transcribe", method="POST", delegate=transcribe_recording)
            ]
        )
    )
    
async def main(): 
    microservice = await TotoMicroservice.init(get_microservice_config())
    port = 8080
    await microservice.start(port=port)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())