"""Deterministic context selection and compilation for agent harnesses."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class ContextItem:
    """A piece of context with stable ID and explicit priority (0 is highest)."""
    id: str
    content: str
    kind: str = "note"
    priority: int = 50
    source: str = "user"
    pinned: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class CompiledContext:
    text: str
    selected_ids: list[str]
    estimated_tokens: int
    omitted_ids: list[str]


class ContextManager:
    """Select context under an approximate token budget using deterministic priorities.

    Token count uses ceil(chars / 4), not a model-specific tokenizer. Replace this
    estimator with a provider tokenizer before enforcing hard production limits.
    """
    def __init__(self, *, max_tokens: int = 4000, chars_per_token: int = 4) -> None:
        if max_tokens < 1 or chars_per_token < 1:
            raise ValueError("max_tokens and chars_per_token must be positive")
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token

    def estimate_tokens(self, text: str) -> int:
        return (len(text) + self.chars_per_token - 1) // self.chars_per_token

    def compile(self, items: Iterable[ContextItem], *, task: str,
                system_instructions: str = "", max_tokens: int | None = None) -> CompiledContext:
        budget = self.max_tokens if max_tokens is None else max_tokens
        if budget < 1:
            raise ValueError("max_tokens must be positive")
        sections = []
        if system_instructions.strip():
            sections.append(f"## SYSTEM INSTRUCTIONS\n{system_instructions.strip()}")
        sections.append(f"## CURRENT TASK\n{task.strip()}")
        text = "\n\n".join(sections)
        used = self.estimate_tokens(text)
        if used > budget:
            raise ValueError(f"Mandatory context needs about {used} tokens, exceeding budget {budget}")

        candidates = sorted(list(items), key=lambda x: (not x.pinned, x.priority, x.id))
        selected, selected_ids = [], []
        for item in candidates:
            section = f"\n\n## {item.kind.upper()} [{item.id}]\n{item.content.strip()}"
            cost = self.estimate_tokens(section)
            if used + cost <= budget:
                text += section
                used += cost
                selected.append(item)
                selected_ids.append(item.id)
        included = set(selected_ids)
        return CompiledContext(text, selected_ids, used,
                               [item.id for item in candidates if item.id not in included])
