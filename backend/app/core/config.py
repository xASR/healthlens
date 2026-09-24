"""
Centralized application settings.

Reads from environment variables / a local .env file (see .env.example).
Import `settings` anywhere you need config instead of re-reading os.environ.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"

    database_url: str = "sqlite:///./healthlens.db"

    firebase_credentials_path: str = "./firebase-service-account.json"
    google_places_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached so we only parse the .env file once per process."""
    return Settings()


settings = get_settings()
