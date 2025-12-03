from typing import Optional

from pydantic import BaseModel, Field, validator


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    username: str = Field(default="demo", min_length=1, max_length=50)

    @validator("message")
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    response: str
    username: str
    customer_id: str
    timestamp: str
    pii_masked: bool = False
    context_retrieved: bool = False


class HealthResponse(BaseModel):
    status: str
    model: str
    langchain_version: str
    rag_enabled: bool
    pii_protection: bool


class UserListResponse(BaseModel):
    users: dict
    count: int
