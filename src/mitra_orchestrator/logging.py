"""Structured logging configuration for controller processes."""

import logging
import sys
from collections.abc import MutableMapping, Sequence
from typing import Any

import structlog

from mitra_orchestrator.config.settings import Settings


def _add_service_context(
    _logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    event_dict["service"] = "mitra-orchestrator"
    return event_dict


def _shared_processors() -> Sequence[structlog.types.Processor]:
    return (
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_service_context,
    )


def configure_logging(settings: Settings) -> None:
    """Configure structlog and standard-library logs with one renderer."""
    renderer: structlog.types.Processor
    if settings.environment.lower() in {"production", "staging"}:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=False)

    shared_processors = _shared_processors()
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            *shared_processors,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # Uvicorn otherwise installs dedicated plaintext handlers. Route all of its
    # records through the same processor formatter as application/dependency logs.
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )
