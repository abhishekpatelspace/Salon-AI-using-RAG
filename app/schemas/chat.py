from typing import List, Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    score: Optional[float] = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = Field(default="default")
    customer_id: Optional[int] = None
    top_k: int = Field(default=4, ge=1, le=10)


class ChatResponse(BaseModel):
    reply: str
    citations: List[Citation] = Field(default_factory=list)
    intent: str = Field(default="chat")
