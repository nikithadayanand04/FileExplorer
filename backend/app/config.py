"""
Configuration management for CryptoFS++ backend.
Centralizes environment variables and system settings.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CryptoFS++"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    ENCRYPTED_DIR: Path = Path("encrypted")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Encryption
    ENCRYPTION_ALGORITHM: str = "AES-256"
    KEY_DERIVATION_ITERATIONS: int = 100000
    
    # AI Classification Thresholds
    LOW_THRESHOLD: int = 30
    MEDIUM_THRESHOLD: int = 60
    HIGH_THRESHOLD: int = 80
    CRITICAL_THRESHOLD: int = 100
    
    # Blockchain
    BLOCKCHAIN_ENABLED: bool = True
    BLOCKCHAIN_FILE: Path = Path("blockchain_ledger.json")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(exist_ok=True)
settings.ENCRYPTED_DIR.mkdir(exist_ok=True)

