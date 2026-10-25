from typing import Sequence
import httpx

from datrixai.core.models import ChatMessage, ChatResponse
from datrixai.core.exceptions import ModelRequestError


class OllamaChatModel:
    """Adapter for Ollama's /api/chat endpoint; tool calling is not yet normalized."""

    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def complete(self, messages: Sequence[ChatMessage]) -> ChatResponse:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
            return ChatResponse(content=data["message"]["content"], raw=data)
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise ModelRequestError(f"Ollama request failed: {exc}") from exc
