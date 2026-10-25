from .documents import Document


def chunk_documents(
    documents: list[Document], *, chunk_size: int = 800, overlap: int = 100
) -> list[Document]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and less than chunk_size")
    chunks = []
    stride = chunk_size - overlap
    for doc in documents:
        text = doc.text
        start = 0
        while start < len(text):
            piece = text[start : start + chunk_size]
            if piece.strip():
                chunks.append(Document(text=piece, source=doc.source, metadata=doc.metadata))
            if start + chunk_size >= len(text):
                break
            start += stride
    return chunks
