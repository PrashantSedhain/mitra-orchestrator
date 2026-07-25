"""Environment-backed application settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated process configuration; secrets must be injected at runtime."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MITRA_",
        extra="ignore",
        case_sensitive=False,
    )

    environment: str = "development"
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
