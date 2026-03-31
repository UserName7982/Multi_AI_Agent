from typing import Optional

from pydantic import BaseModel

class ChatResponse(BaseModel):
    Answer:str
    query:str

class ChatRequest(BaseModel):
    query:str
    Thread:int = 1

class Messages(BaseModel):
    message_id: Optional[str]
    thread_id: str
    role:str
    content:str

class Thread(BaseModel):
    thread_id: Optional[str]
    user_id:str
    title:str

class thread_Response(BaseModel):
    thread_id: str
    message:str

class message_Response(BaseModel):
    message_id: str
    message:str