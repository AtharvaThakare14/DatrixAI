import pytest
from datrixai.rag import Document, LexicalRetriever, RAGPipeline, chunk_documents


def test_chunk_documents_overlap():
    docs = [Document(text="abcdefghij", source="sample.txt")]
    chunks = chunk_documents(docs, chunk_size=6, overlap=2)
    assert [chunk.text for chunk in chunks] == ["abcdef", "efghij"]


def test_chunk_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_documents([Document(text="x", source="x")], chunk_size=5, overlap=5)


def test_retriever_returns_matching_source():
    retriever = LexicalRetriever([
        Document(text="apples and oranges", source="fruit.txt"),
        Document(text="database indexes improve SQL queries", source="db.txt"),
    ])
    result = RAGPipeline(retriever).retrieve("SQL indexes", top_k=1)
    assert result.sources == ["db.txt"]
    assert "database indexes" in result.answer_context


def test_retriever_no_match_is_empty():
    assert LexicalRetriever([Document(text="cats", source="cats.txt")]).search("volcano") == []
