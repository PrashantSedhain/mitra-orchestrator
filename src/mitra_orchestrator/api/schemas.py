"""Public API response schemas."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness response independent of external dependencies."""

    status: Literal["ok"] = "ok"
    service: str
    version: str


class ReadinessResponse(BaseModel):
    """Readiness response with named dependency checks."""

    status: Literal["ready"] = "ready"
    checks: dict[str, str]
