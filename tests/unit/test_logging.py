import json
import logging
from uuid import UUID

from httpx import ASGITransport, AsyncClient
from pytest import CaptureFixture
from structlog.testing import capture_logs

from mitra_orchestrator.api.app import create_app
from mitra_orchestrator.config.settings import Settings
from mitra_orchestrator.logging import configure_logging


def test_production_logging_structures_standard_library_events(
    capsys: CaptureFixture[str],
) -> None:
    configure_logging(Settings(environment="production"))

    logging.getLogger("dependency").warning("dependency warning")

    captured = capsys.readouterr()
    event = json.loads(captured.out)
    assert event["event"] == "dependency warning"
    assert event["level"] == "warning"
    assert event["service"] == "mitra-orchestrator"


async def test_request_logging_uses_server_id_and_records_safe_client_id() -> None:
    app = create_app(Settings(environment="test"))

    with capture_logs() as logs:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/healthz", headers={"X-Request-ID": "client-123"})

    server_request_id = response.headers["X-Request-ID"]
    UUID(server_request_id)
    assert server_request_id != "client-123"
    request_log = logs[-1]
    assert request_log["event"] == "http_request_completed"
    assert request_log["log_level"] == "info"
    assert request_log["method"] == "GET"
    assert request_log["path"] == "/healthz"
    assert request_log["request_id"] == server_request_id
    assert request_log["client_request_id"] == "client-123"
    assert request_log["status_code"] == 200
    assert request_log["duration_ms"] >= 0


async def test_request_logging_does_not_reflect_unsafe_client_id() -> None:
    app = create_app(Settings(environment="test"))

    with capture_logs() as logs:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/healthz", headers={"X-Request-ID": "bad\r\ninjected"})

    UUID(response.headers["X-Request-ID"])
    assert "client_request_id" not in logs[-1]


async def test_request_logging_correlates_unhandled_failures() -> None:
    app = create_app(Settings(environment="test"))

    @app.get("/fails")
    async def fails() -> None:
        raise RuntimeError("sensitive internal failure")

    with capture_logs() as logs:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/fails")

    assert response.status_code == 500
    server_request_id = response.headers["X-Request-ID"]
    UUID(server_request_id)
    failure_log = logs[-1]
    assert failure_log["event"] == "http_request_failed"
    assert failure_log["request_id"] == server_request_id
    assert failure_log["status_code"] == 500
    assert failure_log["duration_ms"] >= 0
