"""
Domain error hierarchy for the RAG pipeline.

No FastAPI / HTTP types — translate to HTTP at the API boundary only.
"""

from __future__ import annotations

from typing import Any, Optional


class RAGDomainError(Exception):
    """Base failure for medical RAG operations (storage, retrieval, generation context)."""

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}


class RAGException(RAGDomainError):
    """Generic RAG pipeline failure (e.g. ingest, vector store operation)."""


class EmbeddingError(RAGDomainError):
    """Embedding model load, encode, or dimension mismatch."""


class DocumentNotFoundError(RAGDomainError):
    """No document matches the requested identifier in the knowledge base."""
