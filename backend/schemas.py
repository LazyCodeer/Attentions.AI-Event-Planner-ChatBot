# schemas.py
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    contact: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    msg: str = None
    email: str


class ChatMessage(BaseModel):
    user_id: str
    message: str
    timestamp: str
