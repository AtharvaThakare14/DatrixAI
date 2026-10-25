class DatrixAIError(Exception):
    """Base exception for framework errors."""


class ModelRequestError(DatrixAIError):
    """Raised when a model provider request fails."""


class ToolExecutionError(DatrixAIError):
    """Raised when a registered tool fails or receives invalid arguments."""
