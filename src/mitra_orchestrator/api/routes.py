"""Operational API routes."""

from fastapi import APIRouter

from mitra_orchestrator import __version__
from mitra_orchestrator.api.schemas import HealthResponse, ReadinessResponse

router = APIRouter(include_in_schema=False)


@router.get("/healthz", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Report process liveness without checking dependencies."""
    return HealthResponse(service="mitra-orchestrator", version=__version__)


@router.get("/readyz", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    """Report readiness; durable dependency checks arrive with Phase 2."""
    return ReadinessResponse(checks={})
