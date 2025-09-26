"""
Configuration settings for MultiToolAPI
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "sqlite:///./data/sqlite/multitoolapi.db"
    redis_url: str = "redis://localhost:6379"  # Optional for simple setup
    
    # Google APIs
    google_api_key: Optional[str] = None
    google_places_api_key: Optional[str] = None
    google_maps_api_key: Optional[str] = None
    
    # Gemini AI
    gemini_api_key: Optional[str] = None
    
    # Vector Database
    chroma_persist_directory: str = "./data/chroma_db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Scraping Configuration
    scraping_delay: float = 1.0
    max_concurrent_requests: int = 5
    user_agent: str = "MultiToolAPI/1.0"
    
    # File Upload
    max_file_size: int = 10485760  # 10MB
    upload_directory: str = "./uploads"
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Application
    debug: bool = True
    project_name: str = "MultiToolAPI"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
