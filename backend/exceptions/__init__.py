"""Application-level exception packages (domain, API mapping in later layers)."""

from .domain import (
    RAGDomainError,
    RAGException,
    EmbeddingError,
    DocumentNotFoundError,
)

__all__ = [
    "RAGDomainError",
    "RAGException",
    "EmbeddingError",
    "DocumentNotFoundError",
]
