import os
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env")
    BASE_PATH: str=os.getcwd()
    DB_URI :str
    DB_URI1 :str
    BetterStack:str
    URI: str
    Linkdin_API:str
    Linkdin_SECRET:str
    Linkdin_ACCESS_TOKEN:str
config=Settings() # type: ignore