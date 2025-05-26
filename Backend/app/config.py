"""
Application configuration using Pydantic settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AKTA - Proposal Archive API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Searchable digital archive for political proposals"
    
    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "akta_user"
    POSTGRES_PASSWORD: str = "akta_password"
    POSTGRES_DB: str = "akta_db"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Configuration
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    
    # Search Configuration
    EMBEDDING_DIMENSION: int = 768
    MAX_SEARCH_RESULTS: int = 100
    DEFAULT_SEARCH_RESULTS: int = 20
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt"}
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Security
    SECRET_KEY: str = "akta-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()