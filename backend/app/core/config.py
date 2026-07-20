"""Application configuration loaded from environment variables.

Secrets such as the OpenAI API key are read only from the environment and are
never hardcoded (SECURITY-12).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_timeout_seconds: float = 60.0

    # Image constraints
    max_image_bytes: int = 10 * 1024 * 1024  # 10 MB

    # CORS: comma separated list of allowed origins
    cors_allow_origins: str = "http://localhost:3000"

    # Local rate limiting
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # Meta
    environment: str = "development"
    app_version: str = "0.1.0"

    @property
    def allowed_origins(self) -> list[str]:
        """Parsed list of allowed CORS origins."""
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def openai_configured(self) -> bool:
        """Whether an OpenAI API key is present."""
        return bool(self.openai_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
