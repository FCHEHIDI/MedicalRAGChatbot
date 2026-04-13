"""
Medical RAG pipeline: orchestrates injected vector store, embeddings, and LLM ports.
No FastAPI / HTTP — domain exceptions only.
"""

from __future__ import annotations

import gc
import sys
from typing import Any, List, Type

try:
    import ollama  # noqa: F401

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from domain.config import RAGConfig
from domain.ports import EmbeddingsPort, LLMPort, VectorStorePort
from exceptions.domain import RAGException

# --- Memory helpers (shared with API for /memory-status) ---


def cleanup_memory() -> int:
    """Force garbage collection to free memory."""
    collected = gc.collect()
    print(f"🧹 Memory cleanup: {collected} objects collected")
    return collected


def get_memory_usage() -> dict[str, Any]:
    """Best-effort process memory info (Windows-friendly)."""
    try:
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                kernel32 = ctypes.windll.kernel32

                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", wintypes.DWORD),
                        ("dwMemoryLoad", wintypes.DWORD),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                memory_status = MEMORYSTATUSEX()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))

                used_mb = (memory_status.ullTotalPhys - memory_status.ullAvailPhys) // (1024 * 1024)
                total_mb = memory_status.ullTotalPhys // (1024 * 1024)

                return {
                    "used_mb": used_mb,
                    "total_mb": total_mb,
                    "available_mb": memory_status.ullAvailPhys // (1024 * 1024),
                    "usage_percent": (used_mb / total_mb) * 100 if total_mb else 0,
                }
            except Exception:
                pass

        return {
            "used_mb": "unknown",
            "total_mb": "unknown",
            "available_mb": "unknown",
            "usage_percent": "unknown",
        }
    except Exception as e:
        return {"error": str(e)}


# --- Core RAG ---


class MedicalRAGSystem:
    """Single responsibility: run the medical RAG pipeline (retrieve + generate)."""

    def __init__(
        self,
        vector_store: VectorStorePort,
        embeddings: EmbeddingsPort,
        llm: LLMPort,
        *,
        config: Type[RAGConfig] = RAGConfig,
    ) -> None:
        print("🚀 Initializing Memory-Optimized Medical RAG System...")
        self._vector_store = vector_store
        self._embeddings = embeddings
        self._llm = llm
        self._config = config
        self.request_count = 0

        cleanup_memory()
        memory_info = get_memory_usage()
        print(f"💾 Initial Memory: {memory_info}")
        print("✅ Medical RAG System ready with memory optimization!")

    @property
    def collection(self) -> Any:
        """Backward compatibility: Chroma collection object when using ChromaVectorStore."""
        return getattr(self._vector_store, "collection", None)

    @property
    def ollama_client(self) -> Any:
        """Backward compatibility for /health (optional client handle)."""
        return getattr(self._llm, "_client", None)

    @property
    def ollama_model(self) -> Any:
        return getattr(self._llm, "_model", None)

    @property
    def ollama_available(self) -> bool:
        return self._llm.is_ready

    def count_documents(self) -> int:
        return self._vector_store.count()

    def add_document(self, content: str, title: str, category: str = "general") -> dict[str, Any]:
        try:
            embedding = self._embeddings.encode_text(content)

            doc_id = f"{category}_{title}_{hash(content) % 10000}"

            self._vector_store.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[
                    {
                        "title": title,
                        "category": category,
                        "content_length": len(content),
                    }
                ],
                ids=[doc_id],
            )

            del embedding
            gc.collect()

            return {"status": "success", "doc_id": doc_id}

        except RAGException:
            raise
        except Exception as e:
            print(f"❌ Document addition error: {e}")
            raise RAGException("Failed to add document") from e

    def search_knowledge(
        self, query: str, n_results: int | None = None
    ) -> dict[str, Any]:
        n = n_results if n_results is not None else self._config.TOP_K_RESULTS
        try:
            query_embedding = self._embeddings.encode_text(query)

            results = self._vector_store.query(
                query_embedding,
                n_results=n,
                include=["documents", "metadatas", "distances"],
            )

            knowledge_context: List[str] = []
            sources: List[dict[str, Any]] = []

            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results["documents"][0] if results["documents"] else [],
                    results["metadatas"][0] if results["metadatas"] else [],
                    results["distances"][0] if results["distances"] else [],
                )
            ):
                if distance < 0.8:
                    knowledge_context.append(f"Source {i+1}: {doc}")
                    source_citation = {
                        "title": metadata.get("title", f"Document {i+1}"),
                        "content": doc[:200] + "..." if len(doc) > 200 else doc,
                        "score": round(1.0 - distance, 3),
                        "metadata": {
                            "category": metadata.get("category", "general"),
                            "content_length": metadata.get("content_length", len(doc)),
                            "full_content": doc,
                        },
                    }
                    sources.append(source_citation)

            del query_embedding, results
            gc.collect()

            return {
                "context": "\n\n".join(knowledge_context),
                "sources": sources,
            }

        except Exception as e:
            print(f"❌ Knowledge search error: {e}")
            return {"context": "", "sources": []}

    def generate_response(self, query: str, context: str) -> str:
        self.request_count += 1

        if self.request_count % self._config.CLEANUP_FREQUENCY == 0:
            cleanup_memory()
            print(f"🧹 Periodic cleanup after {self.request_count} requests")

        system_prompt = """You are a helpful medical assistant. Use the provided context to answer questions accurately and professionally.

If the context doesn't contain relevant information, say so clearly and provide general medical guidance while recommending consultation with healthcare professionals.

IMPORTANT: Always remind users to consult with qualified healthcare professionals for medical advice."""

        prompt = f"""Context from medical knowledge base:
{context}

Question: {query}

Please provide a helpful, accurate response based on the context above:"""

        generated = self._llm.generate(system_prompt, prompt)
        if generated is not None:
            del system_prompt, prompt
            gc.collect()
            return generated

        if context.strip():
            fallback_response = f"""Based on the medical information in our knowledge base:

{context}

For the question: "{query}"

⚠️ This information is from our medical knowledge base and should be used for educational purposes only. Always consult with qualified healthcare professionals for personalized medical advice, diagnosis, or treatment recommendations.

🏥 For emergencies or serious symptoms, seek immediate medical attention."""
        else:
            fallback_response = f"""I don't have specific information about "{query}" in my current knowledge base.

For accurate medical information about this topic, I recommend:
1. Consulting with your healthcare provider
2. Visiting reputable medical websites like WebMD or Mayo Clinic
3. Contacting your doctor's office for guidance

⚠️ MEDICAL DISCLAIMER: Always consult with qualified healthcare professionals for medical concerns, especially for serious symptoms or medical emergencies."""

        gc.collect()
        return fallback_response
