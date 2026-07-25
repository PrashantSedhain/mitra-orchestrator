from mitra_orchestrator.config.settings import Settings


def test_settings_use_safe_local_defaults() -> None:
    settings = Settings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000
