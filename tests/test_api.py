import pytest
from httpx import ASGITransport, AsyncClient
from datrixai.api.app import create_app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_rag_endpoint():
    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url="http://test") as client:
        response = await client.post("/rag/query", json={"query": "RAG retrieves documents"})
    assert response.status_code == 200
    assert response.json()["sources"]
