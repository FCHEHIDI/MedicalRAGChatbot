"""Pytest fixtures: backend on path, TESTING=1, async HTTP client."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import AsyncIterator
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

# Repo root / backend on sys.path (imports: main, domain, api, …)
_ROOT = Path(__file__).resolve().parent.parent
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

os.environ.setdefault("TESTING", "1")


@pytest.fixture
def mock_rag_system() -> MagicMock:
    """Minimal stand-in for MedicalRAGSystem used by routes."""
    m = MagicMock()
    m.ollama_available = False
    m.collection = object()
    m.count_documents.return_value = 3
    m.search_knowledge.return_value = {
        "context": "ctx",
        "sources": [
            {
                "title": "T",
                "content": "c",
                "score": 0.9,
                "metadata": {"category": "general"},
            }
        ],
    }
    m.generate_response.return_value = "mock answer"
    m.add_document.return_value = {"status": "success", "doc_id": "x"}
    m.request_count = 0
    return m


@pytest.fixture
async def async_client(mock_rag_system: MagicMock, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    """httpx.AsyncClient against the FastAPI app (RAG mocked)."""
    import main

    monkeypatch.setattr(main, "rag_system", mock_rag_system)

    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
