
from totoms import (APIConfiguration, TotoEnvironment, TotoMicroserviceConfiguration, TotoMicroservice)
from totoms.TotoMicroservice import APIEndpoint, determine_environment
from totoms.TotoDelegateDecorator import toto_delegate
from config import WhisperConfig

@toto_delegate
async def say_hello(request, user_context, exec_context):
    return {"message": "Hello from Whisper Microservice!"}

def get_microservice_config() -> TotoMicroserviceConfiguration:
    return TotoMicroserviceConfiguration(
        service_name="whisper", 
        environment=TotoEnvironment(
            hyperscaler="aws", 
            hyperscaler_configuration=determine_environment()
        ), 
        custom_config=WhisperConfig, 
        api_configuration=APIConfiguration(
            api_endpoints=[
                APIEndpoint(path="/hello", method="POST", delegate=say_hello)
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