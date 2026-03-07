import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env")
    BASE_PATH: str=os.getcwd()
    Gemini_API_KEY: SecretStr

config=Settings() # type: ignore