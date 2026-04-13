"""Domain layer: RAG pipeline and configuration (no FastAPI)."""

from .rag_system import (
    RAGConfig,
    MedicalRAGSystem,
    cleanup_memory,
    get_memory_usage,
    OLLAMA_AVAILABLE,
    RAGException,
    EmbeddingError,
    DocumentNotFoundError,
)

__all__ = [
    "RAGConfig",
    "MedicalRAGSystem",
    "cleanup_memory",
    "get_memory_usage",
    "OLLAMA_AVAILABLE",
    "RAGException",
    "EmbeddingError",
    "DocumentNotFoundError",
]
