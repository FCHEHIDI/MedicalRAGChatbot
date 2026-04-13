"""
HTTP performance: perf_counter middleware, Prometheus histogram/counter, latency percentiles.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.latency_store import LatencyPercentileStore

# Prometheus (default registry)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Wall-clock latency of HTTP requests (middleware)",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")),
)

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "status_code"],
)

# Shared store for /metrics/latency-summary
latency_store = LatencyPercentileStore()


def _default_skip(path: str) -> bool:
    """Do not skew latency stats with scrape endpoint or static noise."""
    if path.startswith("/metrics"):
        return True
    return path == "/favicon.ico"


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Measures full request time (including inner middleware and route).
    Register first so this middleware is outermost and captures end-to-end latency.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        store: LatencyPercentileStore | None = None,
        skip_predicate: Callable[[str], bool] | None = None,
    ) -> None:
        super().__init__(app)
        self._store = store or latency_store
        self._skip = skip_predicate or _default_skip

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        path = request.url.path
        if self._skip(path):
            return await call_next(request)

        t0 = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            dt = time.perf_counter() - t0
            self._store.record(dt)
            HTTP_REQUEST_DURATION.observe(dt)
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                status_code=str(status),
            ).inc()


def register_observability_routes(app: FastAPI, store: LatencyPercentileStore | None = None) -> None:
    """Mount Prometheus scrape endpoint and JSON latency summary."""
    st = store or latency_store

    @app.get("/metrics", include_in_schema=False)
    async def prometheus_metrics() -> Response:
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    @app.get("/metrics/latency-summary", include_in_schema=False)
    async def latency_summary() -> dict[str, Any]:
        return st.percentiles()
