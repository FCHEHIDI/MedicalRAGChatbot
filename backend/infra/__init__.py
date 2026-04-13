"""Infrastructure: concrete adapters for vector store, embeddings, LLM."""

from domain.ports import EmbeddingsPort, LLMPort, VectorStorePort

from .chroma_vector_store import ChromaVectorStore
from .lcel_medical_rag import build_langchain_chroma, build_medical_lcel_chain
from .ollama_llm import OllamaLLM
from .sentence_transformers_embeddings import SentenceTransformersEmbeddings


def build_default_rag_system():
    """Wire default Chroma + sentence-transformers + Ollama + LCEL chain."""
    from domain.config import RAGConfig
    from domain.rag_system import MedicalRAGSystem

    config = RAGConfig
    vector_store = ChromaVectorStore(config)
    embeddings = SentenceTransformersEmbeddings(config)
    llm = OllamaLLM(config)

    lc_vs = build_langchain_chroma(embeddings, config)
    lcel_chain = build_medical_lcel_chain(lc_vs, llm, config)

    return MedicalRAGSystem(
        vector_store=vector_store,
        embeddings=embeddings,
        llm=llm,
        config=config,
        lcel_chain=lcel_chain,
    )


__all__ = [
    "VectorStorePort",
    "EmbeddingsPort",
    "LLMPort",
    "ChromaVectorStore",
    "SentenceTransformersEmbeddings",
    "OllamaLLM",
    "build_default_rag_system",
    "build_langchain_chroma",
    "build_medical_lcel_chain",
]
