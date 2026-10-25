from fastapi import FastAPI
from datrixai.agents import Agent
from datrixai.core.models import ChatMessage, ChatResponse
from datrixai.rag import Document, LexicalRetriever, RAGPipeline
from .schemas import AgentRunRequest, AgentRunResponse, RAGQueryRequest, RAGQueryResponse


class DemoModel:
    """Deterministic model for smoke tests and demos; replace for real generation."""

    async def complete(self, messages: list[ChatMessage]) -> ChatResponse:
        prompt = messages[-1].content if messages else ""
        return ChatResponse(content=f"Demo response: {prompt}")


def create_app() -> FastAPI:
    app = FastAPI(title="DatrixAI API", version="0.1.0")
    agent = Agent(model=DemoModel(), instructions="Return a short helpful answer.")
    rag = RAGPipeline(
        LexicalRetriever(
            [
                Document(
                    text="DatrixAI is a modular Python framework for AI agents and RAG.",
                    source="builtin:datrixai-intro",
                ),
                Document(
                    text="RAG retrieves relevant documents and passes their context to a language model.",
                    source="builtin:rag-explainer",
                ),
            ]
        )
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "framework": "DatrixAI"}

    @app.post("/agent/run", response_model=AgentRunResponse)
    async def run_agent(request: AgentRunRequest) -> AgentRunResponse:
        result = await agent.run(request.prompt)
        return AgentRunResponse(output=result.output, steps=result.steps)

    @app.post("/rag/query", response_model=RAGQueryResponse)
    async def query_rag(request: RAGQueryRequest) -> RAGQueryResponse:
        result = rag.retrieve(request.query, top_k=request.top_k)
        return RAGQueryResponse(context=result.answer_context, sources=result.sources)

    return app


app = create_app()
