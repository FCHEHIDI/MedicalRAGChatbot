"""SentenceTransformers adapter implementing EmbeddingsPort."""

from __future__ import annotations

from typing import Type

import gc
from sentence_transformers import SentenceTransformer

from domain.config import RAGConfig
from exceptions.domain import EmbeddingError


class SentenceTransformersEmbeddings:
    """Local sentence-transformers model (CPU)."""

    def __init__(self, config: Type[RAGConfig] = RAGConfig) -> None:
        try:
            print("📚 Loading embedding model with memory optimization...")
            print(f"🔄 Downloading {config.EMBEDDING_MODEL} (first time may take 2-3 minutes)...")
            self._model = SentenceTransformer(
                config.EMBEDDING_MODEL,
                cache_folder="./models_cache",
                device="cpu",
            )
            if hasattr(self._model, "_modules"):
                gc.collect()
            print("✅ Embedding model loaded with memory optimization!")
        except Exception as e:
            print(f"❌ Embedding setup error: {e}")
            raise EmbeddingError("Embedding model initialization failed") from e

    def encode_text(self, text: str) -> list[float]:
        vec = self._model.encode(
            [text],
            convert_to_tensor=False,
            normalize_embeddings=True,
            batch_size=1,
        )[0]
        return vec.tolist()
