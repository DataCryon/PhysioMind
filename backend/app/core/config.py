"""
Application configuration using pydantic-settings.
Loads environment variables from .env file with validation.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Groq LLM
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # Google Gemini (Embeddings)
    GOOGLE_API_KEY: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_BUCKET: str = "pdfs"
    SUPABASE_VECTOR_TABLE: str = "doc_chunks"

    # Embedding
    EMBEDDING_MODEL: str = "models/gemini-embedding-2"
    EMBEDDING_DIMENSION: int = 384

    # RAG parameters
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 5

    # Server
    FRONTEND_URL: str = "http://localhost:5173"
    LOG_LEVEL: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton to avoid re-reading .env on every access."""
    return Settings()
