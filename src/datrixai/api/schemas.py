from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)


class AgentRunResponse(BaseModel):
    output: str
    steps: int


class RAGQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10_000)
    top_k: int = Field(default=3, ge=1, le=10)


class RAGQueryResponse(BaseModel):
    context: str
    sources: list[str]
