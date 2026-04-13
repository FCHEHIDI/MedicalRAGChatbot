"""Infrastructure: concrete adapters for vector store, embeddings, LLM."""

from domain.ports import EmbeddingsPort, LLMPort, VectorStorePort

from .chroma_vector_store import ChromaVectorStore
from .ollama_llm import OllamaLLM
from .sentence_transformers_embeddings import SentenceTransformersEmbeddings


def build_default_rag_system():
    """Wire default Chroma + sentence-transformers + Ollama stack."""
    from domain.config import RAGConfig
    from domain.rag_system import MedicalRAGSystem

    config = RAGConfig
    return MedicalRAGSystem(
        vector_store=ChromaVectorStore(config),
        embeddings=SentenceTransformersEmbeddings(config),
        llm=OllamaLLM(config),
        config=config,
    )


__all__ = [
    "VectorStorePort",
    "EmbeddingsPort",
    "LLMPort",
    "ChromaVectorStore",
    "SentenceTransformersEmbeddings",
    "OllamaLLM",
    "build_default_rag_system",
]
