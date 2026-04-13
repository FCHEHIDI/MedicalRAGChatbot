"""Ollama HTTP client adapter implementing LLMPort."""

from __future__ import annotations

import logging
from typing import Any, Type

from domain.config import RAGConfig
from resilience.circuit_breaker import SimpleCircuitBreaker
from resilience.exceptions import CircuitOpenError
from resilience.sync_call import resilient_sync

logger = logging.getLogger("medical_rag.ollama")

try:
    import ollama

    _OLLAMA_IMPORT_OK = True
    print("✅ Ollama library imported successfully")
except ImportError:
    ollama = None  # type: ignore[assignment, unused-ignore]
    _OLLAMA_IMPORT_OK = False
    print("⚠️ Ollama not available - will use fallback mode")


class OllamaLLM:
    """Local LLM via Ollama; falls back when unavailable."""

    def __init__(self, config: Type[RAGConfig] = RAGConfig) -> None:
        self._config = config
        self._client: Any = None
        self._model: str | None = None
        self._breaker = SimpleCircuitBreaker(
            "ollama_llm",
            failure_threshold=config.CIRCUIT_FAILURE_THRESHOLD,
            recovery_seconds=config.CIRCUIT_RECOVERY_SECONDS,
        )

        if not _OLLAMA_IMPORT_OK:
            print("⚠️ Ollama not installed - using fallback mode")
            return

        try:
            assert ollama is not None
            self._client = ollama.Client(host=config.OLLAMA_HOST)
            try:
                models = self._client.list()
                available_models = [m["name"] for m in models["models"]]
                print(f"📦 Available Ollama models: {available_models}")

                if "llama3.2:3b" in available_models:
                    self._model = "llama3.2:3b"
                elif "llama3.2:1b" in available_models:
                    self._model = "llama3.2:1b"
                else:
                    print("⚠️ No models found - will use fallback responses")
                    self._model = None

                if self._model:
                    print(f"🤖 Using Ollama model: {self._model}")
            except Exception as model_error:
                print(f"⚠️ Model setup issue: {model_error}")
                print("🔄 Using fallback mode instead")
                self._model = None
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("🔄 Using fallback mode - RAG will still work!")
            self._client = None
            self._model = None

    @property
    def is_ready(self) -> bool:
        return bool(_OLLAMA_IMPORT_OK and self._client and self._model)

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.is_ready:
            return None

        assert self._client is not None and self._model is not None

        def _call() -> str:
            response = self._client.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response["message"]["content"]

        try:
            return resilient_sync(
                "ollama_chat",
                self._breaker,
                _call,
                timeout_sec=self._config.LLM_TIMEOUT_SECONDS,
                max_attempts=self._config.LLM_RETRY_MAX,
                min_wait=self._config.LLM_RETRY_MIN_WAIT,
                max_wait=self._config.LLM_RETRY_MAX_WAIT,
            )
        except CircuitOpenError:
            logger.warning("ollama circuit open; skipping direct chat")
            return None
        except TimeoutError:
            logger.warning("ollama chat timed out after retries")
            return None
        except Exception as e:
            print(f"❌ Ollama generation error: {e}")
            print("🔄 Falling back to simple response...")
            return None
