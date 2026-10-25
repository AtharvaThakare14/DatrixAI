import pytest
from datrixai.agents import Agent, tool
from datrixai.core.models import ChatResponse, ToolCall
from datrixai.core.exceptions import ToolExecutionError


class FakeModel:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    async def complete(self, messages):
        self.calls += 1
        return next(self.responses)


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


@pytest.mark.asyncio
async def test_agent_executes_registered_tool_then_answers():
    model = FakeModel([
        ChatResponse(content="", tool_calls=[ToolCall("multiply", {"a": 6, "b": 7})]),
        ChatResponse(content="42"),
    ])
    result = await Agent(model=model, tools=[multiply]).run("What is 6 times 7?")
    assert result.output == "42"
    assert result.steps == 2
    assert result.tool_results[0]["result"] == 42


@pytest.mark.asyncio
async def test_agent_rejects_unregistered_tool():
    model = FakeModel([ChatResponse(content="", tool_calls=[ToolCall("danger", {})])])
    with pytest.raises(ToolExecutionError, match="unregistered"):
        await Agent(model=model).run("do something")


def test_agent_bounds_steps():
    with pytest.raises(ValueError):
        Agent(model=FakeModel([]), max_steps=100)
