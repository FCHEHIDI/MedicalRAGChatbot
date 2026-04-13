"""Rolling window of request latencies for percentile summaries (P50 / P95 / P99)."""

from __future__ import annotations

import threading
from collections import deque
from typing import Any


class LatencyPercentileStore:
    """Thread-safe store with fixed max samples (oldest dropped)."""

    def __init__(self, max_samples: int = 10_000) -> None:
        self._max = max_samples
        self._latencies: deque[float] = deque(maxlen=max_samples)
        self._lock = threading.Lock()

    def record(self, seconds: float) -> None:
        if seconds < 0:
            return
        with self._lock:
            self._latencies.append(seconds)

    def percentiles(self) -> dict[str, Any]:
        with self._lock:
            if not self._latencies:
                return {
                    "count": 0,
                    "p50_ms": 0.0,
                    "p95_ms": 0.0,
                    "p99_ms": 0.0,
                }
            s = sorted(self._latencies)
            n = len(s)

            def rank(p: float) -> float:
                if n == 1:
                    return float(s[0])
                idx = min(int(round(p * (n - 1))), n - 1)
                return float(s[idx])

            return {
                "count": n,
                "p50_ms": round(rank(0.50) * 1000, 3),
                "p95_ms": round(rank(0.95) * 1000, 3),
                "p99_ms": round(rank(0.99) * 1000, 3),
            }
