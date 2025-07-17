from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings."""
    
    APP_NAME: str = "FastAPI Demo Project"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database settings (for future use)
    DATABASE_URL: str = "sqlite:///./test.db"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 