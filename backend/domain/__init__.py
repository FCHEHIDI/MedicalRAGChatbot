"""Domain layer: RAG pipeline and configuration (no FastAPI)."""

from exceptions.domain import (
    RAGDomainError,
    RAGException,
    EmbeddingError,
    DocumentNotFoundError,
)

from .rag_system import (
    RAGConfig,
    MedicalRAGSystem,
    cleanup_memory,
    get_memory_usage,
    OLLAMA_AVAILABLE,
)

__all__ = [
    "RAGConfig",
    "MedicalRAGSystem",
    "cleanup_memory",
    "get_memory_usage",
    "OLLAMA_AVAILABLE",
    "RAGDomainError",
    "RAGException",
    "EmbeddingError",
    "DocumentNotFoundError",
]
