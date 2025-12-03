from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer_id: str


class TokenData(BaseModel):
    username: Optional[str] = None
    customer_id: Optional[str] = None


class UserProfile(BaseModel):
    customer_id: str
    username: str
    email: str
    full_name: Optional[str]
    created_at: str
