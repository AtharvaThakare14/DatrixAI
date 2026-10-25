import json
from typing import Sequence
import httpx

from datrixai.core.models import ChatMessage, ChatResponse, ToolCall
from datrixai.core.exceptions import ModelRequestError


class OpenAICompatibleChatModel:
    """Chat adapter for APIs implementing the OpenAI /v1/chat/completions shape."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def complete(self, messages: Sequence[ChatMessage]) -> ChatResponse:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=payload
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ModelRequestError(f"OpenAI-compatible model request failed: {exc}") from exc

        try:
            choice = data["choices"][0]["message"]
            content = choice.get("content") or ""
            tool_calls = []
            for item in choice.get("tool_calls", []):
                fn = item.get("function", {})
                args = json.loads(fn.get("arguments") or "{}")
                tool_calls.append(ToolCall(name=fn["name"], arguments=args))
            return ChatResponse(content=content, tool_calls=tool_calls, raw=data)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ModelRequestError("Provider returned an unsupported chat-completion response") from exc
