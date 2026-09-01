from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class TicketCreate(BaseModel):
    title: str
    description: str = ""


class AgentRequest(BaseModel):
    message: str = Field(min_length=1)
