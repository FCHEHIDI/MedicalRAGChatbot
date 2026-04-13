"""Domain layer: RAG pipeline, config, ports (no FastAPI)."""

from exceptions.domain import (
    DocumentNotFoundError,
    EmbeddingError,
    RAGDomainError,
    RAGException,
)

from .config import RAGConfig
from .ports import EmbeddingsPort, LLMPort, VectorStorePort
from .rag_system import (
    OLLAMA_AVAILABLE,
    MedicalRAGSystem,
    cleanup_memory,
    get_memory_usage,
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
    "VectorStorePort",
    "EmbeddingsPort",
    "LLMPort",
]
