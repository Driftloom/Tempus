"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str
    database_echo: bool = False
    database_ssl_mode: str = "require"  # disable, allow, prefer, require, verify-ca, verify-full
    database_ssl_root_cert: str | None = None

    # Redis
    redis_url: str

    # LLM Providers
    ollama_host: str = "http://localhost:11434"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Security
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    encryption_key: str

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


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
