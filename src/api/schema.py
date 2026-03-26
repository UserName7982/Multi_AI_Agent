from pydantic import BaseModel

class ChatResponse(BaseModel):
    Answer:str
    query:str

class ChatRequest(BaseModel):
    query:str
    Thread:int = 1