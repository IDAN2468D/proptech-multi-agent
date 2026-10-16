import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

trace_id_ctx_var: ContextVar[str] = ContextVar("trace_id", default="")


def get_trace_id() -> str:
    """Return current request/execution trace ID or generate one."""
    tid = trace_id_ctx_var.get()
    if not tid:
        tid = str(uuid.uuid4())
        trace_id_ctx_var.set(tid)
    return tid


def set_trace_id(trace_id: str | None = None) -> str:
    """Set and return a trace ID for the current execution context."""
    tid = trace_id or str(uuid.uuid4())
    trace_id_ctx_var.set(tid)
    return tid


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line structured JSON with trace_id."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "trace_id": get_trace_id(),
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            payload.update(record.extra_data)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure root/application structured JSON logger."""
    logger = logging.getLogger("proptech")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = configure_logging()
