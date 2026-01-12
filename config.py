
from totoms import TotoControllerConfig


class WhisperConfig(TotoControllerConfig): 
    def get_mongo_secret_names(self):
        return None