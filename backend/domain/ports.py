"""
Ports (Protocols) — defined in domain so infrastructure depends on domain, not the reverse.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class VectorStorePort(Protocol):
    """Abstract vector persistence + similarity search."""

    def add(
        self,
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        ...

    def query(
        self,
        query_embedding: list[float],
        *,
        n_results: int,
        include: list[str],
    ) -> dict[str, Any]:
        ...

    def count(self) -> int:
        ...


@runtime_checkable
class EmbeddingsPort(Protocol):
    """Text → dense vectors for retrieval."""

    def encode_text(self, text: str) -> list[float]:
        ...


@runtime_checkable
class LLMPort(Protocol):
    """Optional chat completion (e.g. local Ollama)."""

    @property
    def is_ready(self) -> bool:
        ...

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        ...
