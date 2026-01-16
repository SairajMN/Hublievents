"""
Configuration management for Hublievents Backend API.
Environment-based settings with secure secret handling.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import secrets


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./hublievents.db")
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"])
    ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])

    # File Upload
    UPLOAD_PATH: str = Field(default="uploads")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = Field(default_factory=lambda: ["image/jpeg", "image/png", "image/webp"])

    # Email (future use)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # WhatsApp (future use)
    WHATSAPP_API_KEY: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None

    # Redis (future caching)
    REDIS_URL: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW: int = Field(default=60)  # seconds

    # Admin
    ADMIN_EMAIL: str = Field(default="admin@hublievents.com")
    ADMIN_PASSWORD: str = Field(default="ChangeThisInProduction123!")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v, values):
        """Assemble PostgreSQL URL from individual components if not provided."""
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v

        # Build PostgreSQL URL from components
        postgres_host = values.get("POSTGRES_HOST")
        postgres_port = values.get("POSTGRES_PORT")
        postgres_user = values.get("POSTGRES_USER")
        postgres_password = values.get("POSTGRES_PASSWORD")
        postgres_db = values.get("POSTGRES_DB")

        if all([postgres_host, postgres_port, postgres_user, postgres_password, postgres_db]):
            return f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

        # Default to SQLite for development
        return v or "sqlite:///./hublievents.db"

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse ALLOWED_HOSTS from comma-separated string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    @validator("ALLOWED_IMAGE_TYPES", pre=True)
    def parse_allowed_image_types(cls, v):
        """Parse ALLOWED_IMAGE_TYPES from comma-separated string or list."""
        if isinstance(v, str):
            return [img_type.strip() for img_type in v.split(",")]
        return v

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


# Global settings instance
settings = Settings()
