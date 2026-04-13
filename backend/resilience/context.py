"""Async-safe request correlation for logging outside the HTTP layer."""

from __future__ import annotations

import contextvars
from typing import Optional

request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id",
    default=None,
)
