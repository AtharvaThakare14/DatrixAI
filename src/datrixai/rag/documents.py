from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Document:
    text: str
    source: str
    metadata: dict[str, str] = field(default_factory=dict)


def load_text_files(paths: list[str | Path]) -> list[Document]:
    """Load UTF-8 text and Markdown files. Does not execute or parse uploaded code."""
    docs = []
    for item in paths:
        path = Path(item)
        if path.suffix.lower() not in {".txt", ".md", ".markdown"}:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        docs.append(Document(text=path.read_text(encoding="utf-8"), source=str(path)))
    return docs
