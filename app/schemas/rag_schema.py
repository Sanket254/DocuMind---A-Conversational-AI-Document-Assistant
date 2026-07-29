from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    conversation_id: int | None = None
    top_k: int = 5
    stream: bool = False
    summarize: bool = False


class QueryResponse(BaseModel):
    answer: str
    summary: str | None = None