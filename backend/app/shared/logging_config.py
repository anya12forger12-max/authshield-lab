"""Structured logging configuration using structlog."""

from __future__ import annotations

import logging
import sys
import time
from typing import Any

import structlog

_initialized = False


def setup_logging(
    log_level: str = "DEBUG",
    json_output: bool = False,
) -> None:
    """Configure structlog and stdlib logging for the application.

    Parameters
    ----------
    log_level:
        Minimum log level (e.g. ``DEBUG``, ``INFO``).
    json_output:
        When ``True`` emit JSON; otherwise emit human-readable console output.
    """
    global _initialized  # noqa: PLW0603
    if _initialized:
        return
    _initialized = True

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_output:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty())

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.DEBUG)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(message)s")
        )
        root.addHandler(handler)


def get_logger(name: str | None = None, **initial_context: Any) -> structlog.stdlib.BoundLogger:
    """Return a structlog-bound logger.

    Parameters
    ----------
    name:
        Optional logger name / module identifier.
    **initial_context:
        Extra key-value pairs attached to every log entry from this logger.

    Returns
    -------
    structlog.stdlib.BoundLogger
    """
    return structlog.get_logger(name, **initial_context)  # type: ignore[return-value]


def log_security_event(
    event: str,
    *,
    logger: structlog.stdlib.BoundLogger | None = None,
    **kwargs: Any,
) -> None:
    """Emit a security-classified log entry.

    Parameters
    ----------
    event:
        Security event description.
    logger:
        Optional pre-bound logger; a fresh one is created if ``None``.
    **kwargs:
        Additional context fields.
    """
    log = logger or get_logger("security")
    log.warning(event, tag="security", **kwargs)


def log_audit_event(
    event: str,
    *,
    user_id: str | None = None,
    action: str = "",
    resource: str = "",
    logger: structlog.stdlib.BoundLogger | None = None,
    **kwargs: Any,
) -> None:
    """Emit an audit-classified log entry for compliance tracking.

    Parameters
    ----------
    event:
        Audit event description.
    user_id:
        ID of the user performing the action.
    action:
        Short verb describing the action (e.g. ``CREATE``, ``DELETE``).
    resource:
        Target resource identifier.
    logger:
        Optional pre-bound logger.
    **kwargs:
        Additional context fields.
    """
    log = logger or get_logger("audit")
    log.info(
        event,
        tag="audit",
        user_id=user_id,
        action=action,
        resource=resource,
        **kwargs,
    )


def log_performance_event(
    event: str,
    duration_ms: float,
    *,
    logger: structlog.stdlib.BoundLogger | None = None,
    **kwargs: Any,
) -> None:
    """Emit a performance timing log entry.

    Parameters
    ----------
    event:
        Description of the measured operation.
    duration_ms:
        Elapsed time in milliseconds.
    logger:
        Optional pre-bound logger.
    **kwargs:
        Additional context fields.
    """
    log = logger or get_logger("performance")
    log.info(
        event,
        tag="performance",
        duration_ms=round(duration_ms, 2),
        **kwargs,
    )


class RequestLoggingMiddleware:
    """Simple ASGI middleware that logs request/response timing via structlog.

    This is a lightweight implementation intended to be wired into the FastAPI
    app as raw ASGI middleware.
    """

    def __init__(self, app: Any) -> None:  # noqa: ANN401
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:  # noqa: ANN401
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        log = get_logger("http")
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        start = time.perf_counter()

        await self.app(scope, receive, send)

        duration_ms = (time.perf_counter() - start) * 1000
        log.info(
            "request_completed",
            method=method,
            path=path,
            duration_ms=round(duration_ms, 2),
        )
