"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    cors_origins: list[str] = ["http://localhost:3000"]
    model_dir: str = "app/models"

    model_config = {"env_file": ".env"}


settings = Settings()
