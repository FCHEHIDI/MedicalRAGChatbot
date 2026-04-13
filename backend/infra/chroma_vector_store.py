"""ChromaDB adapter implementing VectorStorePort."""

from __future__ import annotations

from typing import Any, Type

import chromadb
from chromadb.config import Settings

from domain.config import RAGConfig
from exceptions.domain import RAGException


class ChromaVectorStore:
    """Persistent Chroma collection for medical RAG."""

    def __init__(self, config: Type[RAGConfig] = RAGConfig) -> None:
        try:
            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
            self._client = chromadb.PersistentClient(
                path=config.CHROMADB_PATH,
                settings=settings,
            )
            self.collection = self._client.get_or_create_collection(
                name=config.COLLECTION_NAME,
                metadata={
                    "description": "Free medical RAG knowledge base",
                    "hnsw:space": "cosine",
                    "hnsw:batch_size": 100,
                    "hnsw:sync_threshold": 1000,
                },
            )
            print("✅ ChromaDB initialized with memory optimization!")
        except Exception as e:
            print(f"❌ ChromaDB setup error: {e}")
            raise RAGException("Database initialization failed") from e

    def add(
        self,
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def query(
        self,
        query_embedding: list[float],
        *,
        n_results: int,
        include: list[str],
    ) -> dict[str, Any]:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=include,
        )

    def count(self) -> int:
        return self.collection.count()
