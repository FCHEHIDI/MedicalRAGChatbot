"""
Synchronous resilient calls: exponential backoff retries, optional timeout, logging with request_id.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Any, Callable, TypeVar

from tenacity import retry, stop_after_attempt, wait_exponential

from resilience.circuit_breaker import SimpleCircuitBreaker
from resilience.context import request_id_ctx
from resilience.exceptions import CircuitOpenError

logger = logging.getLogger("medical_rag.resilience")

T = TypeVar("T")


def call_with_timeout(fn: Callable[..., T], timeout_sec: float, *args: Any, **kwargs: Any) -> T:
    """Run sync `fn` in a worker thread with a wall-clock timeout (works on Windows)."""
    with ThreadPoolExecutor(max_workers=1) as pool:
        fut = pool.submit(fn, *args, **kwargs)
        return fut.result(timeout=timeout_sec)


def resilient_sync(
    operation: str,
    breaker: SimpleCircuitBreaker,
    fn: Callable[..., T],
    *,
    fn_args: tuple[Any, ...] = (),
    fn_kwargs: dict[str, Any] | None = None,
    timeout_sec: float | None = None,
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 8.0,
) -> T:
    """
    Retry with exponential backoff; optional per-attempt timeout; circuit breaker accounting.
    Raises last exception after retries exhausted (or CircuitOpenError if breaker blocks).
    """
    fn_kwargs = fn_kwargs or {}
    rid = request_id_ctx.get(None)

    if not breaker.allow():
        logger.warning(
            "circuit_open name=%s operation=%s request_id=%s",
            breaker.name,
            operation,
            rid,
        )
        raise CircuitOpenError(breaker.name)

    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        reraise=True,
    )
    def _inner() -> T:
        if timeout_sec is not None and timeout_sec > 0:
            return call_with_timeout(fn, timeout_sec, *fn_args, **fn_kwargs)
        return fn(*fn_args, **fn_kwargs)

    try:
        out = _inner()
        breaker.record_success()
        return out
    except FuturesTimeout as e:
        logger.exception(
            "resilience_timeout name=%s operation=%s request_id=%s",
            breaker.name,
            operation,
            rid,
        )
        breaker.record_failure()
        raise TimeoutError(f"{operation}_timeout") from e
    except Exception as e:
        logger.exception(
            "resilience_failure name=%s operation=%s request_id=%s err=%s",
            breaker.name,
            operation,
            rid,
            e,
        )
        breaker.record_failure()
        raise
