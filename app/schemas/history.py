from pydantic import BaseModel
from datetime import datetime


class ConversationCreate(BaseModel):
    title: str | None = None


class MessageCreate(BaseModel):
    conversation_id: int
    role: str
    content: str


class ConversationResponse(BaseModel):
    id: int
    title: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True