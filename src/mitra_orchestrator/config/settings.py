"""Environment-backed application settings."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


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

    postgres_host: str = "127.0.0.1"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_database: str = "mitra"
    postgres_user: str = "mitra"
    postgres_password: SecretStr = SecretStr("change-me-before-use")

    @property
    def database_url(self) -> URL:
        """Build a typed URL without parsing interpolated secret text."""
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_database,
        )
