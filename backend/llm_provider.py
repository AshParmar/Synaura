from __future__ import annotations

import json
import os
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any
from urllib import request as urllib_request


def _to_text(message: Any) -> str:
    return getattr(message, "content", str(message))


def _to_role(message: Any) -> str:
    msg_type = getattr(message, "type", "user")
    if msg_type in {"human", "user"}:
        return "user"
    if msg_type in {"system", "developer"}:
        return "system"
    return "assistant"


@dataclass
class LocalOllamaChat:
    temperature: float = 0.2
    model: str = "llama3"
    host: str = "http://localhost:11434"

    def _chat(self, messages: list[Any]) -> SimpleNamespace:
        payload = {
            "model": self.model,
            "messages": [
                {"role": _to_role(m), "content": _to_text(m)} for m in messages
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
        }
        url = f"{self.host.rstrip('/')}/api/chat"
        req = urllib_request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib_request.urlopen(req, timeout=600) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = ""
        if isinstance(data, dict):
            if isinstance(data.get("message"), dict):
                content = data["message"].get("content", "")
            else:
                content = data.get("response", "")
        return SimpleNamespace(content=content)

    def invoke(self, messages: list[Any]):
        return self._chat(messages)

    def generate(self, messages: Any, **_: Any):
        if isinstance(messages, list) and messages and isinstance(messages[0], list):
            messages = messages[0]
        return self._chat(messages)


def make_llm(
    temperature: float = 0.2,
    model_name: str | None = None,
    prefer_local: bool | None = None,
):
    """Create either a Groq chat model or a local Ollama-backed model."""
    use_local = prefer_local if prefer_local is not None else os.getenv("USE_LOCAL_LLM", "0") == "1"
    if use_local:
        return LocalOllamaChat(
            temperature=temperature,
            model=os.getenv("LOCAL_LLM_MODEL", model_name or "llama3"),
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        )

    from langchain_groq import ChatGroq

    return ChatGroq(
        temperature=temperature,
        model=model_name or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        api_key=os.getenv("GROQ_API_KEY"),
    )