"""FastAPI application factory."""

from fastapi import FastAPI

from mitra_orchestrator import __version__
from mitra_orchestrator.api.routes import router
from mitra_orchestrator.config.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an isolated application instance for serving or tests."""
    resolved_settings = settings or Settings()
    app = FastAPI(
        title="Mitra Orchestrator",
        summary="Durable AI software-engineering control plane",
        version=__version__,
    )
    app.state.settings = resolved_settings
    app.include_router(router)
    return app
