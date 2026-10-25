from typing import Protocol, Sequence
from .models import ChatMessage, ChatResponse


class ChatModel(Protocol):
    async def complete(self, messages: Sequence[ChatMessage]) -> ChatResponse:
        """Return a model response for the supplied conversation."""
        ...
