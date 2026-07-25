"""HTTP request logging and correlation middleware."""

import re
from time import monotonic
from uuid import uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

logger = structlog.get_logger(__name__)
_SAFE_CLIENT_REQUEST_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Emit one structured terminal event for every HTTP request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        server_request_id = str(uuid4())
        supplied_request_id = request.headers.get("X-Request-ID", "")
        client_request_id = (
            supplied_request_id
            if _SAFE_CLIENT_REQUEST_ID.fullmatch(supplied_request_id) is not None
            else None
        )
        started = monotonic()
        context: dict[str, object] = {
            "method": request.method,
            "path": request.url.path,
            "request_id": server_request_id,
        }
        if client_request_id is not None:
            context["client_request_id"] = client_request_id
        request_logger = logger.bind(**context)

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((monotonic() - started) * 1000, 3)
            request_logger.error(
                "http_request_failed",
                status_code=500,
                duration_ms=duration_ms,
                exception_type=type(exc).__name__,
            )
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
        else:
            request_logger.info(
                "http_request_completed",
                status_code=response.status_code,
                duration_ms=round((monotonic() - started) * 1000, 3),
            )

        response.headers["X-Request-ID"] = server_request_id
        return response
