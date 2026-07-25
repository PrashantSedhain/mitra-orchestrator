"""Console entry point for the controller API."""

import uvicorn

from mitra_orchestrator.config.settings import Settings


def main() -> None:
    """Run the API with environment-backed settings."""
    settings = Settings()
    uvicorn.run(
        "mitra_orchestrator.api.app:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
