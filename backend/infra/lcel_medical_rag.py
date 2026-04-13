"""
LangChain 0.3+ LCEL: retriever | prompt | llm | StrOutputParser (no LLMChain / .run()).
Uses langchain-community (Chroma, ChatOllama) + langchain-core runnables.
"""

from __future__ import annotations

from operator import itemgetter
from typing import Any, Type

from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough

from domain.config import RAGConfig
from domain.ports import EmbeddingsPort
from .langchain_embedding_adapter import EmbeddingsPortAdapter
from .ollama_llm import OllamaLLM


def _format_docs(docs: list[Any]) -> str:
    return "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)


def build_langchain_chroma(
    embeddings_port: EmbeddingsPort,
    config: Type[RAGConfig] = RAGConfig,
    *,
    chroma_client: Any | None = None,
) -> Chroma:
    """Réutilise le PersistentClient de ChromaVectorStore si fourni (sinon conflit singleton LangChain)."""
    adapter = EmbeddingsPortAdapter(embeddings_port)
    if chroma_client is not None:
        return Chroma(
            client=chroma_client,
            collection_name=config.COLLECTION_NAME,
            embedding_function=adapter,
        )
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        persist_directory=config.CHROMADB_PATH,
        embedding_function=adapter,
    )


def build_ollama_chat_model(llm_port: OllamaLLM, config: Type[RAGConfig] = RAGConfig) -> ChatOllama | None:
    """ChatOllama for LCEL when LLM_PROVIDER=ollama."""
    if not llm_port.is_ready or not llm_port._model:
        return None
    return ChatOllama(
        model=llm_port._model,
        base_url=config.OLLAMA_HOST,
        temperature=0.2,
        timeout=int(config.LLM_TIMEOUT_SECONDS),
    )


def build_groq_chat_model(config: Type[RAGConfig] = RAGConfig) -> BaseChatModel | None:
    """ChatGroq for LCEL when LLM_PROVIDER=groq."""
    if not config.GROQ_API_KEY:
        return None
    try:
        from langchain_groq import ChatGroq
    except ImportError:
        print("⚠️ langchain-groq not installed — pip install langchain-groq")
        return None
    return ChatGroq(
        model_name=config.GROQ_MODEL,
        groq_api_key=config.GROQ_API_KEY,
        temperature=0.2,
        request_timeout=int(config.LLM_TIMEOUT_SECONDS),
    )


def build_medical_lcel_chain(
    lc_vectorstore: Chroma,
    config: Type[RAGConfig],
    *,
    chat_model: BaseChatModel | None,
) -> Runnable | None:
    """
    LCEL: retriever | prompt | BaseChatModel | StrOutputParser (Ollama ou Groq).
    """
    if chat_model is None:
        print("⚠️ LCEL chain skipped — no chat model")
        return None

    retriever = lc_vectorstore.as_retriever(
        search_kwargs={"k": config.TOP_K_RESULTS},
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful medical assistant. Use the provided context to answer "
                "accurately and professionally. If the context does not contain relevant "
                "information, say so and recommend consulting healthcare professionals. "
                "Always remind users to consult qualified healthcare professionals for medical advice.",
            ),
            (
                "human",
                "Context from medical knowledge base:\n{context}\n\n"
                "Question: {question}\n\n"
                "Please provide a helpful, accurate response based on the context above:",
            ),
        ]
    )

    chain: Runnable = (
        RunnablePassthrough.assign(
            context=itemgetter("question") | retriever | RunnableLambda(_format_docs)
        )
        | prompt
        | chat_model
        | StrOutputParser()
    )

    print("✅ LCEL medical RAG chain ready (retriever | prompt | chat LLM | StrOutputParser)")
    return chain
