from __future__ import annotations

import os
from typing import Any

from config import OPENROUTER_API_KEY


class LLMClient:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self._client = None

    def _ensure(self):
        if os.getenv("DRY_RUN") == "1":
            return None
        if self._client is None:
            if not self.api_key:
                raise RuntimeError(
                    "OPENROUTER_API_KEY not set; cannot call LLM (unset DRY_RUN to require)"
                )
            from openrouter import OpenRouterClient  # lazy import

            self._client = OpenRouterClient(api_key=self.api_key)
        return self._client

    def chat(self, model: str, messages: list[dict[str, Any]]) -> str:
        if os.getenv("DRY_RUN") == "1":
            # Simple deterministic stub for tests/demos
            last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            return f"[DRY_RUN:{model}] {last_user}"
        if not model or not isinstance(messages, list) or not messages:
            raise ValueError("Invalid LLM request: model and messages are required")
        client = self._ensure()
        try:
            resp = client.chat.completions.create(model=model, messages=messages)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"LLM request failed for model '{model}': {exc}") from exc
        # Safely unwrap content
        try:
            return resp.choices[0].message.content  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            msg = "Unexpected LLM response shape: " "missing choices/message.content"
            raise RuntimeError(msg) from exc


client = LLMClient(OPENROUTER_API_KEY)
