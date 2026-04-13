"""ChromaDB adapter implementing VectorStorePort."""

from __future__ import annotations

from typing import Any, Type

import chromadb
from chromadb.config import Settings

from domain.config import RAGConfig
from exceptions.domain import RAGException
from resilience.circuit_breaker import SimpleCircuitBreaker
from resilience.exceptions import CircuitOpenError
from resilience.sync_call import resilient_sync


class ChromaVectorStore:
    """Persistent Chroma collection for medical RAG."""

    def __init__(self, config: Type[RAGConfig] = RAGConfig) -> None:
        self._config = config
        self._breaker = SimpleCircuitBreaker(
            "chroma_vector",
            failure_threshold=config.CIRCUIT_FAILURE_THRESHOLD,
            recovery_seconds=config.CIRCUIT_RECOVERY_SECONDS,
        )
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
        def _run() -> None:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )

        try:
            resilient_sync(
                "chroma_add",
                self._breaker,
                _run,
                timeout_sec=self._config.VECTOR_TIMEOUT_SECONDS,
                max_attempts=self._config.VECTOR_RETRY_MAX,
                min_wait=self._config.LLM_RETRY_MIN_WAIT,
                max_wait=self._config.LLM_RETRY_MAX_WAIT,
            )
        except CircuitOpenError as e:
            raise RAGException("Vector store temporarily unavailable (circuit open)") from e
        except TimeoutError as e:
            raise RAGException("Vector store operation timed out") from e
        except Exception as e:
            raise RAGException("Failed to add to vector store") from e

    def query(
        self,
        query_embedding: list[float],
        *,
        n_results: int,
        include: list[str],
    ) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=include,
            )

        try:
            return resilient_sync(
                "chroma_query",
                self._breaker,
                _run,
                timeout_sec=self._config.VECTOR_TIMEOUT_SECONDS,
                max_attempts=self._config.VECTOR_RETRY_MAX,
                min_wait=self._config.LLM_RETRY_MIN_WAIT,
                max_wait=self._config.LLM_RETRY_MAX_WAIT,
            )
        except CircuitOpenError as e:
            raise RAGException("Vector store temporarily unavailable (circuit open)") from e
        except TimeoutError as e:
            raise RAGException("Vector store query timed out") from e
        except Exception as e:
            raise RAGException("Vector store query failed") from e

    def count(self) -> int:
        def _run() -> int:
            return self.collection.count()

        try:
            return resilient_sync(
                "chroma_count",
                self._breaker,
                _run,
                timeout_sec=self._config.VECTOR_TIMEOUT_SECONDS,
                max_attempts=self._config.VECTOR_RETRY_MAX,
                min_wait=self._config.LLM_RETRY_MIN_WAIT,
                max_wait=self._config.LLM_RETRY_MAX_WAIT,
            )
        except CircuitOpenError as e:
            raise RAGException("Vector store temporarily unavailable (circuit open)") from e
        except TimeoutError as e:
            raise RAGException("Vector store count timed out") from e
        except Exception as e:
            raise RAGException("Vector store count failed") from e
