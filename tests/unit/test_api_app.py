from httpx import ASGITransport, AsyncClient

from mitra_orchestrator.api.app import create_app
from mitra_orchestrator.config.settings import Settings


async def test_health_endpoint_identifies_service() -> None:
    app = create_app(Settings(environment="test"))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "mitra-orchestrator",
        "version": "0.1.0",
    }


async def test_readiness_endpoint_reports_current_checks() -> None:
    app = create_app(Settings(environment="test"))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "checks": {}}
