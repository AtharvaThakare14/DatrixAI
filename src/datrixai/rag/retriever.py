import re
from dataclasses import dataclass
from .documents import Document


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))


@dataclass(frozen=True)
class RAGResult:
    answer_context: str
    sources: list[str]
    documents: list[Document]


class LexicalRetriever:
    """Small dependency-free lexical retriever; not semantic/vector search."""

    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents

    def search(self, query: str, *, top_k: int = 3) -> list[Document]:
        if top_k < 1:
            raise ValueError("top_k must be positive")
        query_tokens = _tokens(query)
        scored = []
        for index, document in enumerate(self.documents):
            overlap = len(query_tokens & _tokens(document.text))
            if overlap:
                scored.append((overlap, -index, document))
        scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
        return [item[2] for item in scored[:top_k]]


class RAGPipeline:
    def __init__(self, retriever: LexicalRetriever) -> None:
        self.retriever = retriever

    def retrieve(self, query: str, *, top_k: int = 3) -> RAGResult:
        documents = self.retriever.search(query, top_k=top_k)
        context = "\n\n".join(
            f"[Source: {doc.source}]\n{doc.text}" for doc in documents
        )
        return RAGResult(
            answer_context=context,
            sources=list(dict.fromkeys(doc.source for doc in documents)),
            documents=documents,
        )
