from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class ChatResponse(BaseModel):
    Answer:str
    query:str

class ChatRequest(BaseModel):
    query:str
    Thread:int = 1

class Messages(BaseModel):
    message_id: Optional[UUID]=None
    thread_id: UUID
    role:str
    content:str

class Thread(BaseModel):
    thread_id: Optional[UUID]=None
    user_id:str
    title:str

class thread_Response(BaseModel):
    thread_id: UUID
    message:str

class message_Response(BaseModel):
    message_id: UUID
    message:str