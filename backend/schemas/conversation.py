from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid


class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: int
    title: str
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []


class ChatRequestWithConversation(BaseModel):
    message: str
    conversation_id: Optional[int] = None  # If None, create new conversation
    conversation_title: Optional[str] = None  # For new conversations


class ChatResponseWithConversation(BaseModel):
    response: str
    conversation_id: int
    conversation_title: str
