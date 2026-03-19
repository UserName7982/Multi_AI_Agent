from typing import TypedDict

class RetrivalState(TypedDict):
    USER_QUERY: str
    SENTACTIC_QUERY: str
    SEMANTIC_QUERY: str
    IMAGE_QUERY: str
    LLM_RESPONSE: str
    error: str