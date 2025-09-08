from pydantic import BaseModel
from typing import List, Dict

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class StreamChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]
