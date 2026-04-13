"""HTTP API: middleware X-Request-ID, validation handlers, Prometheus metrics."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_root(async_client: AsyncClient) -> None:
    r = await async_client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "running"


@pytest.mark.asyncio
async def test_request_id_echo(async_client: AsyncClient) -> None:
    r = await async_client.get("/", headers={"X-Request-ID": "trace-abc-123"})
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID") == "trace-abc-123"


@pytest.mark.asyncio
async def test_validation_error_includes_request_id(async_client: AsyncClient) -> None:
    r = await async_client.post("/chat", json={})
    assert r.status_code == 422
    data = r.json()
    assert "detail" in data
    assert data.get("code") == "validation_error"
    assert data.get("request_id")


@pytest.mark.asyncio
async def test_metrics_prometheus_text(async_client: AsyncClient) -> None:
    r = await async_client.get("/metrics")
    assert r.status_code == 200
    body = r.text
    assert "http_requests_total" in body or "http_request_duration_seconds" in body


@pytest.mark.asyncio
async def test_latency_summary_json(async_client: AsyncClient) -> None:
    r = await async_client.get("/metrics/latency-summary")
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert "p50_ms" in data
    assert "p95_ms" in data
    assert "p99_ms" in data


@pytest.mark.asyncio
async def test_metrics_increment_after_requests(async_client: AsyncClient) -> None:
    for _ in range(3):
        await async_client.get("/health")
    r = await async_client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text


@pytest.mark.asyncio
async def test_chat_with_mock_rag(async_client: AsyncClient) -> None:
    r = await async_client.post("/chat", json={"message": "What is diabetes?"})
    assert r.status_code == 200
    body = r.json()
    assert body["response"] == "mock answer"
    assert body["conversation_id"] == "default"
