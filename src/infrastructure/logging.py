"""
Centralised logging configuration.

All logging in this project flows through structlog. stdlib loggers (uvicorn,
sqlalchemy, httpx, …) are routed through structlog as well so every log line
shares the same format and carries the same context variables.

Extension points
----------------
The `_build_processors()` function lists explicit hook points where future
integrations should be added:

* **Sentry** — add `sentry_sdk.integrations.logging.EventHandler` to the
  stdlib root logger *or* insert a structlog processor that calls
  `sentry_sdk.capture_event` for ERROR+ entries.  Either approach works;
  the structlog processor route gives finer-grained control over what gets
  sent.

* **OpenTelemetry** — insert `opentelemetry.instrumentation.structlog` (or a
  custom processor) right after `merge_contextvars` so that the active span's
  trace_id/span_id are injected into every log record.  The request-id context
  variable set by `RequestLoggingMiddleware` provides a correlation handle
  until OTel is wired in.

* **Datadog / Splunk / Loki** — the JSON renderer used in production emits
  ECS-compatible output.  Point your log shipper (Fluent Bit, Vector, …) at
  stdout and it will parse the JSON lines without further configuration.
"""

import logging
import logging.config
import sys
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.config import get_settings

_settings = get_settings()


# ── Processor pipeline ───────────────────────────────────────────────────────


def _build_processors() -> list:
    processors: list = [
        # Merge context variables bound with structlog.contextvars.bind_contextvars()
        # into every log record.  This is how request_id (and future trace_id) flows
        # through all log lines within a single request without explicit passing.
        structlog.contextvars.merge_contextvars,

        # ── Extension point: OpenTelemetry ────────────────────────────────────
        # from opentelemetry.instrumentation.structlog import OpenTelemetryProcessor
        # OpenTelemetryProcessor(),

        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),

        # ── Extension point: Sentry ───────────────────────────────────────────
        # _sentry_processor,   # call sentry_sdk.capture_event for ERROR+

        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]
    return processors


def _build_renderer():
    if _settings.ENVIRONMENT == "development":
        return structlog.dev.ConsoleRenderer(colors=True)
    # JSON in production — compatible with Datadog, Splunk, Loki, CloudWatch
    return structlog.processors.JSONRenderer()


# ── Public setup function ────────────────────────────────────────────────────


def setup_logging() -> None:
    """Configure structlog and route stdlib logging through it.

    Call this once, as early as possible at application startup, before any
    logger is used.
    """
    log_level = logging.DEBUG if _settings.DEBUG else logging.INFO

    shared_processors = _build_processors()

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            _build_renderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # Silence noisy library loggers unless DEBUG is on
    _noisy = {
        "uvicorn.access": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,
        "sqlalchemy.pool": logging.WARNING,
    }
    for name, level in _noisy.items():
        logging.getLogger(name).setLevel(
            logging.DEBUG if _settings.DEBUG else level
        )


# ── Request logging middleware ────────────────────────────────────────────────


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Attach a unique request_id to every log line within a request.

    The request_id is stored in structlog's contextvars so it automatically
    appears in all log entries produced during that request — no explicit
    passing required.

    When OpenTelemetry is added, replace (or supplement) request_id with the
    OTel trace_id so logs and traces correlate in your observability platform.
    """

    _log = structlog.get_logger()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=str(uuid.uuid4()),
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)

        self._log.info(
            "request",
            status_code=response.status_code,
        )
        return response
