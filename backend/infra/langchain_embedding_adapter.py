"""Bridge domain EmbeddingsPort → LangChain Embeddings (same vectors as ingest)."""

from __future__ import annotations

from langchain_core.embeddings import Embeddings

from domain.ports import EmbeddingsPort


class EmbeddingsPortAdapter(Embeddings):
    """Wraps our SentenceTransformers-backed port for LangChain vector stores."""

    def __init__(self, port: EmbeddingsPort) -> None:
        self._port = port

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._port.encode_text(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._port.encode_text(text)
