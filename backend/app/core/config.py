from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Union
import os

# Get the backend directory path (one level up from app directory)
BACKEND_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Parseon"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Frontend
    NEXT_PUBLIC_API_URL: str = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-16k")  # Default model with 16k context window
    
    # Database - Modified for Railway deployment support
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_POOL_SIZE: int = int(os.getenv("REDIS_POOL_SIZE", "10"))
    REDIS_POOL_TIMEOUT: int = int(os.getenv("REDIS_POOL_TIMEOUT", "30"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    # CORS - Updated for deployment
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = None
    
    # Cache
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    EMBEDDING_CACHE_TTL: int = int(os.getenv("EMBEDDING_CACHE_TTL", "86400"))  # 24 hours
    
    # API Keys Rotation
    API_KEY_ROTATION_DAYS: int = int(os.getenv("API_KEY_ROTATION_DAYS", "30"))
    
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),  # This will look for .env in the backend directory
        case_sensitive=True
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Parse CORS origins from environment variable if it exists
        cors_origins_env = os.getenv("BACKEND_CORS_ORIGINS", "")
        if cors_origins_env:
            self.BACKEND_CORS_ORIGINS = cors_origins_env.split(",")
        else:
            # Default allowed origins
            self.BACKEND_CORS_ORIGINS = [
                "http://localhost:3000",  # Next.js frontend
                "http://127.0.0.1:3000",  # Alternative localhost
                "http://localhost:8000",  # FastAPI backend
                "http://127.0.0.1:8000",  # Alternative localhost
                "https://parseon.vercel.app",  # Vercel deployment
                "https://*.vercel.app",  # All Vercel preview deployments
            ]
            
        # Use DATABASE_URL from Railway if available
        railway_db_url = os.getenv("DATABASE_URL")
        if railway_db_url and not self.DATABASE_URL:
            self.DATABASE_URL = railway_db_url

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 