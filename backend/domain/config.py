"""RAG runtime configuration (no side effects)."""


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
