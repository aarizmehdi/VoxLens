"""
VoxLens — Application Configuration

All settings are loaded from environment variables with sensible defaults.
Uses Pydantic Settings for type-safe, validated configuration.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the VoxLens backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    debug: bool = False
    log_level: str = "INFO"

    # --- Database ---
    database_url: str = "sqlite:///./voxlens.db"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- DeepSeek LLM ---
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"


    # --- Whisper ---
    whisper_model_size: str = "base"

    # --- Embeddings ---
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_persist_dir: str = "./chroma_data"

    # --- Media ---
    upload_dir: str = "./uploads"
    media_dir: str = "./media"
    max_file_size_mb: int = 500
    audio_chunk_duration_seconds: int = 300

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def media_path(self) -> Path:
        path = Path(self.media_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def chroma_path(self) -> Path:
        path = Path(self.chroma_persist_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
