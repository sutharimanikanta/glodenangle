from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    groq_api_key: str = ""
    gold_api_key: str = ""
    backend_url: str = "http://localhost:8000"
    database_url: str = "sqlite+aiosqlite:///./gold_advisor.db"
    app_env: str = "development"
    app_secret_key: str = "dev_secret_change_in_production"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
