"""Minimal circuit breaker (closed / open / half-open) for I/O boundaries."""

from __future__ import annotations

import threading
import time


class SimpleCircuitBreaker:
    """
    After `failure_threshold` consecutive failures, opens for `recovery_seconds`,
    then allows a single probe (half-open). Success closes; failure re-opens.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        name: str,
        *,
        failure_threshold: int = 5,
        recovery_seconds: float = 30.0,
    ) -> None:
        self.name = name
        self._threshold = failure_threshold
        self._recovery = recovery_seconds
        self._failures = 0
        self._state = self.CLOSED
        self._opened_at: float | None = None
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    def allow(self) -> bool:
        with self._lock:
            if self._state == self.CLOSED:
                return True
            if self._state == self.OPEN:
                if self._opened_at is not None:
                    if time.monotonic() - self._opened_at >= self._recovery:
                        self._state = self.HALF_OPEN
                        return True
                return False
            if self._state == self.HALF_OPEN:
                return True
            return False

    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = self.CLOSED
            self._opened_at = None

    def record_failure(self) -> None:
        with self._lock:
            if self._state == self.HALF_OPEN:
                self._state = self.OPEN
                self._opened_at = time.monotonic()
                self._failures = 0
                return
            self._failures += 1
            if self._failures >= self._threshold:
                self._state = self.OPEN
                self._opened_at = time.monotonic()
                self._failures = 0
