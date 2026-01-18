"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    cors_origins: list[str] = ["http://localhost:3000"]
    model_dir: str = "app/models"

    # Pinecone settings (optional - CBR disabled if not set)
    pinecone_api_key: str = ""
    pinecone_index_host: str = ""

    # OpenRouter settings (LLM reasoning)
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    app_url: str = "https://toiturelv-cortex.railway.app"

    model_config = {"env_file": "backend/.env", "extra": "ignore"}


settings = Settings()
