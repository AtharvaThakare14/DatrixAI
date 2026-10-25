import json
from dataclasses import dataclass, field
from typing import Any, Sequence

from datrixai.core.models import ChatMessage
from datrixai.core.protocols import ChatModel
from datrixai.core.exceptions import ToolExecutionError
from .tools import Tool


@dataclass
class AgentResult:
    output: str
    steps: int
    tool_results: list[dict[str, Any]] = field(default_factory=list)


class Agent:
    """Bounded tool-using agent. Only explicitly registered tools may execute."""

    def __init__(
        self,
        *,
        model: ChatModel,
        instructions: str = "You are a helpful assistant.",
        tools: Sequence[Tool] = (),
        max_steps: int = 5,
    ) -> None:
        if max_steps < 1 or max_steps > 20:
            raise ValueError("max_steps must be between 1 and 20")
        self.model = model
        self.instructions = instructions
        self.tools = {item.name: item for item in tools}
        self.max_steps = max_steps

    async def run(self, prompt: str) -> AgentResult:
        messages = [
            ChatMessage("system", self.instructions),
            ChatMessage("user", prompt),
        ]
        history: list[dict[str, Any]] = []
        for step in range(1, self.max_steps + 1):
            response = await self.model.complete(messages)
            if not response.tool_calls:
                return AgentResult(output=response.content, steps=step, tool_results=history)

            messages.append(ChatMessage("assistant", response.content or "[tool call]"))
            for call in response.tool_calls:
                registered = self.tools.get(call.name)
                if registered is None:
                    raise ToolExecutionError(f"Model requested unregistered tool: {call.name}")
                result = await registered.execute(call.arguments)
                history.append({"tool": call.name, "result": result})
                messages.append(
                    ChatMessage(
                        "user",
                        f"Tool result for {call.name}: {json.dumps(result, default=str)}",
                    )
                )
        raise ToolExecutionError(
            f"Agent reached max_steps={self.max_steps} without a final answer"
        )
