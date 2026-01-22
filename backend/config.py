"""
Configuration management for the Intelligent Data Room backend.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google Gemini API
    gemini_api_key: str
    
    # File Upload Settings
    max_file_size_mb: int = 10
    upload_dir: str = "./uploads"
    allowed_extensions: str = "csv,xlsx"    
    # Context Management
    context_window_size: int = 5
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions into a list."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    def ensure_upload_dir(self):
        """Create upload directory if it doesn't exist."""
        os.makedirs(self.upload_dir, exist_ok=True)


# Global settings instance
settings = Settings()