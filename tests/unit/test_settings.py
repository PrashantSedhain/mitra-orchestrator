from pydantic import SecretStr
from sqlalchemy import make_url

from mitra_orchestrator.config.settings import Settings


def test_settings_use_safe_local_defaults() -> None:
    settings = Settings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000
    assert settings.postgres_host == "127.0.0.1"
    assert settings.postgres_port == 5432
    assert settings.postgres_database == "mitra"
    assert settings.postgres_user == "mitra"


def test_database_url_preserves_reserved_values_without_string_reparsing() -> None:
    settings = Settings(
        postgres_host="::1",
        postgres_database="db/name %",
        postgres_user="mitra@ops",
        postgres_password=SecretStr("p@ss:/%#"),
    )

    url = settings.database_url
    assert url.drivername == "postgresql+asyncpg"
    assert url.username == "mitra@ops"
    assert url.password == "p@ss:/%#"
    assert url.host == "::1"
    assert url.port == 5432
    assert url.database == "db/name %"
    rendered = url.render_as_string(hide_password=False)
    assert rendered.startswith("postgresql+asyncpg://mitra%40ops:p%40ss%3A%2F%25%23@[::1]:5432/")
    round_tripped = make_url(rendered)
    assert round_tripped.username == url.username
    assert round_tripped.password == url.password
    assert round_tripped.host == url.host
    assert round_tripped.port == url.port
    assert round_tripped.database == url.database
