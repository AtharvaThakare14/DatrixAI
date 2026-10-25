"""Append-only local JSONL memory store for a single local user/process."""
import json
from pathlib import Path
from .context import ContextItem


class JsonlMemoryStore:
    def __init__(self, path: str | Path = ".datrixai/memory.jsonl") -> None:
        self.path = Path(path)

    def add(self, item: ContextItem) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {"id": item.id, "content": item.content, "kind": item.kind,
                  "priority": item.priority, "source": item.source, "pinned": item.pinned,
                  "created_at": item.created_at}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def list(self, *, limit: int = 100) -> list[ContextItem]:
        if limit < 1:
            raise ValueError("limit must be positive")
        if not self.path.exists():
            return []
        items = [ContextItem(**json.loads(line)) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return items[-limit:]

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
