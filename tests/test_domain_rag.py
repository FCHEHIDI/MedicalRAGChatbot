"""Domain MedicalRAGSystem with mocked ports (no Chroma / Ollama)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_BACKEND = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from domain.config import RAGConfig
from domain.rag_system import MedicalRAGSystem


def test_medical_rag_add_document_uses_ports() -> None:
    vs = MagicMock()
    emb = MagicMock()
    emb.encode_text.return_value = [0.01] * 8
    llm = MagicMock()
    llm.is_ready = False
    llm.generate.return_value = None

    sys = MedicalRAGSystem(vs, emb, llm, config=RAGConfig, lcel_chain=None)
    out = sys.add_document("hello body", "Title", "general")

    assert out["status"] == "success"
    emb.encode_text.assert_called_once()
    vs.add.assert_called_once()


def test_medical_rag_search_formats_sources() -> None:
    vs = MagicMock()
    vs.query.return_value = {
        "documents": [["full doc text"]],
        "metadatas": [[{"title": "Doc1", "category": "x", "content_length": 12}]],
        "distances": [[0.5]],
    }
    emb = MagicMock()
    emb.encode_text.return_value = [0.0] * 4
    llm = MagicMock()
    llm.is_ready = False

    sys = MedicalRAGSystem(vs, emb, llm, config=RAGConfig)
    result = sys.search_knowledge("q")

    assert "full doc text" in result["context"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["score"] == pytest.approx(0.5, rel=0.01)
