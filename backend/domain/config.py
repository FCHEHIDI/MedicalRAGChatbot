"""RAG runtime configuration (no side effects)."""

import os


class RAGConfig:
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODEL = "llama3.2:1b"

    CHROMADB_PATH = "./chroma_db"
    COLLECTION_NAME = "medical_knowledge"

    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    TOP_K_RESULTS = 3
    MAX_CONTEXT_LENGTH = 1000
    BATCH_SIZE = 1

    CLEANUP_FREQUENCY = 10
    MAX_CACHE_SIZE = 50

    # Resilience (LLM + vector store)
    LLM_TIMEOUT_SECONDS = float(os.environ.get("LLM_TIMEOUT_SECONDS", "120"))
    LLM_RETRY_MAX = int(os.environ.get("LLM_RETRY_MAX", "3"))
    LLM_RETRY_MIN_WAIT = float(os.environ.get("LLM_RETRY_MIN_WAIT", "1"))
    LLM_RETRY_MAX_WAIT = float(os.environ.get("LLM_RETRY_MAX_WAIT", "8"))
    VECTOR_TIMEOUT_SECONDS = float(os.environ.get("VECTOR_TIMEOUT_SECONDS", "30"))
    VECTOR_RETRY_MAX = int(os.environ.get("VECTOR_RETRY_MAX", "3"))
    CIRCUIT_FAILURE_THRESHOLD = int(os.environ.get("CIRCUIT_FAILURE_THRESHOLD", "5"))
    CIRCUIT_RECOVERY_SECONDS = float(os.environ.get("CIRCUIT_RECOVERY_SECONDS", "30"))
