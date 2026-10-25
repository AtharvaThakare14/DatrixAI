import inspect
from dataclasses import dataclass
from typing import Any, Callable, get_type_hints

from datrixai.core.exceptions import ToolExecutionError


@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]

    async def execute(self, arguments: dict[str, Any]) -> Any:
        try:
            result = self.function(**arguments)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as exc:
            raise ToolExecutionError(f"Tool '{self.name}' failed: {exc}") from exc

    def schema(self) -> dict[str, Any]:
        hints = get_type_hints(self.function)
        properties = {}
        required = []
        for name, parameter in inspect.signature(self.function).parameters.items():
            annotation = hints.get(name, str)
            json_type = {str: "string", int: "integer", float: "number", bool: "boolean"}.get(
                annotation, "string"
            )
            properties[name] = {"type": json_type}
            if parameter.default is inspect.Parameter.empty:
                required.append(name)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
            },
        }


def tool(function: Callable[..., Any]) -> Tool:
    """Register a trusted Python function as a tool."""
    return Tool(
        name=function.__name__,
        description=inspect.getdoc(function) or function.__name__,
        function=function,
    )
