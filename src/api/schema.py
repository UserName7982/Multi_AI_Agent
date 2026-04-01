from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

class ChatResponse(BaseModel):
    Answer:str
    query:str

class ChatRequest(BaseModel):
    query:str
    Thread:int = 1

class Messages(BaseModel):
    thread_id: UUID = Field(description="Enter Your Thread_ID")
    role:str
    content:str

class Message_Response(BaseModel):
    thread_id: UUID
    role:str
    content:str
    created_at:Optional[datetime]=None
    message_id:UUID

class Thread(BaseModel):
    user_id:str
    title:str

class Thread_Response(BaseModel):
    user_id:str
    title:str
    thread_id:UUID
    created_at:Optional[datetime]=None
