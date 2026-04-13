"""Circuit breaker and resilient_sync (retry + timeout path)."""

from __future__ import annotations

import sys
from concurrent.futures import TimeoutError as FuturesTimeout
from pathlib import Path
import pytest

_BACKEND = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from resilience.circuit_breaker import SimpleCircuitBreaker
from resilience.exceptions import CircuitOpenError
from resilience.sync_call import resilient_sync


def test_circuit_breaker_opens_after_threshold() -> None:
    cb = SimpleCircuitBreaker("test", failure_threshold=2, recovery_seconds=3600.0)
    assert cb.allow() is True
    cb.record_failure()
    cb.record_failure()
    assert cb.allow() is False
    assert cb.state == "open"


def test_circuit_closes_on_success_after_half_open() -> None:
    cb = SimpleCircuitBreaker("test2", failure_threshold=1, recovery_seconds=0.01)
    cb.record_failure()
    assert cb.state == "open"
    # recovery window
    import time

    time.sleep(0.02)
    assert cb.allow() is True
    cb.record_success()
    assert cb.state == "closed"


def test_resilient_sync_retries_then_succeeds() -> None:
    cb = SimpleCircuitBreaker("retry", failure_threshold=10, recovery_seconds=60.0)
    state = {"n": 0}

    def flaky() -> str:
        state["n"] += 1
        if state["n"] < 2:
            raise ConnectionError("transient")
        return "ok"

    out = resilient_sync(
        "flaky_op",
        cb,
        flaky,
        max_attempts=5,
        min_wait=0.01,
        max_wait=0.05,
    )
    assert out == "ok"
    assert state["n"] == 2


def test_resilient_sync_circuit_open_fast_fail() -> None:
    cb = SimpleCircuitBreaker("block", failure_threshold=1, recovery_seconds=3600.0)
    cb.record_failure()

    def never_called() -> str:
        raise AssertionError("should not run")

    with pytest.raises(CircuitOpenError):
        resilient_sync("noop", cb, never_called, max_attempts=1)


def test_call_with_timeout_raises() -> None:
    from resilience import sync_call as sc

    def slow() -> str:
        import time

        time.sleep(10)
        return "x"

    with pytest.raises((FuturesTimeout, TimeoutError)):
        sc.call_with_timeout(slow, 0.05)
