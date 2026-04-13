"""
LangChain 0.3+ LCEL: retriever | prompt | llm | StrOutputParser (no LLMChain / .run()).
Uses langchain-community (Chroma, ChatOllama) + langchain-core runnables.
"""

from __future__ import annotations

from operator import itemgetter
from typing import Any, Type

from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
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
) -> Chroma:
    """Attach to the same persisted collection as ChromaVectorStore."""
    adapter = EmbeddingsPortAdapter(embeddings_port)
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        persist_directory=config.CHROMADB_PATH,
        embedding_function=adapter,
    )


def build_medical_lcel_chain(
    lc_vectorstore: Chroma,
    llm_port: OllamaLLM,
    config: Type[RAGConfig] = RAGConfig,
) -> Runnable | None:
    """
    LCEL: assign context via retriever → ChatPrompt → ChatOllama → StrOutputParser.
    Returns None if no Ollama model is available.
    """
    if not llm_port.is_ready:
        print("⚠️ LCEL chain skipped — Ollama model not available")
        return None

    model = llm_port._model
    assert model is not None

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

    llm = ChatOllama(
        model=model,
        base_url=config.OLLAMA_HOST,
        temperature=0.2,
        timeout=int(config.LLM_TIMEOUT_SECONDS),
    )

    chain: Runnable = (
        RunnablePassthrough.assign(
            context=itemgetter("question") | retriever | RunnableLambda(_format_docs)
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    print("✅ LCEL medical RAG chain ready (retriever | prompt | ChatOllama | StrOutputParser)")
    return chain
