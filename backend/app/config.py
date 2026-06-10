"""Application Configuration"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    APP_NAME: str = "Ahsan Homeo Clinic Management System"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    RELOAD: bool = True
    
    # Database Configuration
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:8000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Clinic Configuration
    CLINIC_NAME: str = "Ahsan Homeo Clinic & Store"
    CLINIC_LOCATION: str = "Karachi, Pakistan"
    ONLINE_CONSULTATION_FEE: int = 500  # PKR
    CLINIC_PHONE: str = "03001234567"
    CLINIC_EMAIL: str = "clinic@ahsanhomeo.com"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
