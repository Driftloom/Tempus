"""Application configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql+asyncpg://tempus:tempus_password@localhost:5432/tempus"
    database_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # LLM Providers
    ollama_host: str = "http://localhost:11434"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    
    # Security
    jwt_secret: str = "your-jwt-secret-key-min-32-characters"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    encryption_key: str = "your-encryption-key-min-32-characters"
    
    # OAuth2
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/api/v1/auth/oauth/callback/google"
    
    outlook_oauth_client_id: str = ""
    outlook_oauth_client_secret: str = ""
    outlook_oauth_redirect_uri: str = "http://localhost:8000/api/v1/auth/oauth/callback/outlook"
    
    # Application
    tempus_env: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
