import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env")
    BASE_PATH: str=os.getcwd()
    DB_URI :str
    DB_URI1 :str
    BetterStack:str
config=Settings() # type: ignore