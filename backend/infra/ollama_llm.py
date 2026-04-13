"""Ollama HTTP client adapter implementing LLMPort."""

from __future__ import annotations

from typing import Any, Type

from domain.config import RAGConfig

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
        try:
            assert self._client is not None and self._model is not None
            response = self._client.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"❌ Ollama generation error: {e}")
            print("🔄 Falling back to simple response...")
            return None
