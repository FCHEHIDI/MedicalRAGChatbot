"""Groq Cloud LLM (OpenAI-compatible chat) for LLMPort — used when LLM_PROVIDER=groq."""

from __future__ import annotations

import logging
from typing import Any, Type

from domain.config import RAGConfig
from resilience.circuit_breaker import SimpleCircuitBreaker
from resilience.exceptions import CircuitOpenError
from resilience.sync_call import resilient_sync

logger = logging.getLogger("medical_rag.groq")

try:
    from groq import Groq

    _GROQ_IMPORT_OK = True
except ImportError:
    Groq = None  # type: ignore[misc, assignment]
    _GROQ_IMPORT_OK = False


class GroqLLM:
    """Groq API via official SDK; implements LLMPort."""

    def __init__(self, config: Type[RAGConfig] = RAGConfig) -> None:
        self._config = config
        self._client: Any = None
        self._model: str = config.GROQ_MODEL
        self._breaker = SimpleCircuitBreaker(
            "groq_llm",
            failure_threshold=config.CIRCUIT_FAILURE_THRESHOLD,
            recovery_seconds=config.CIRCUIT_RECOVERY_SECONDS,
        )

        if not _GROQ_IMPORT_OK:
            print("⚠️ groq package not installed — pip install groq")
            return
        if not config.GROQ_API_KEY:
            print("⚠️ GROQ_API_KEY missing — set it for LLM_PROVIDER=groq")
            return
        self._client = Groq(api_key=config.GROQ_API_KEY)
        print(f"🤖 Groq LLM configured (model={self._model})")

    @property
    def is_ready(self) -> bool:
        return bool(_GROQ_IMPORT_OK and self._client and self._model)

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.is_ready:
            return None

        assert self._client is not None

        def _call() -> str:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            msg = completion.choices[0].message.content
            return msg if msg is not None else ""

        try:
            return resilient_sync(
                "groq_chat",
                self._breaker,
                _call,
                timeout_sec=self._config.LLM_TIMEOUT_SECONDS,
                max_attempts=self._config.LLM_RETRY_MAX,
                min_wait=self._config.LLM_RETRY_MIN_WAIT,
                max_wait=self._config.LLM_RETRY_MAX_WAIT,
            )
        except CircuitOpenError:
            logger.warning("groq circuit open")
            return None
        except TimeoutError:
            logger.warning("groq timed out")
            return None
        except Exception as e:
            print(f"❌ Groq generation error: {e}")
            return None
