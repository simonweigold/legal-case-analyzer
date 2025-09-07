"""
Pydantic models for the Legal Case Analyzer API with Supabase integration.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Sequence
from uuid import UUID
from pydantic import BaseModel, Field
from langchain.schema.messages import BaseMessage


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="The user's message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to continue an existing conversation")


class StreamChatRequest(BaseModel):
    """Request model for streaming chat endpoint."""
    message: str = Field(..., description="The user's message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to continue an existing conversation")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="The AI assistant's response")
    conversation_id: str = Field(..., description="The conversation ID")


class MessageModel(BaseModel):
    """Model for a chat message."""
    id: Optional[str] = None
    role: str = Field(..., description="The role of the message sender (user, assistant, system, tool)")
    content: str = Field(..., description="The content of the message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class ConversationModel(BaseModel):
    """Model for a conversation."""
    id: Optional[str] = None
    user_id: Optional[str] = None
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConversationWithMessages(ConversationModel):
    """Conversation model with messages included."""
    messages: List[MessageModel] = Field(default_factory=list)


class CreateConversationRequest(BaseModel):
    """Request model for creating a new conversation."""
    title: Optional[str] = Field(None, description="Optional title for the conversation")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional metadata for the conversation")


class UpdateConversationRequest(BaseModel):
    """Request model for updating a conversation."""
    title: Optional[str] = Field(None, description="Updated title for the conversation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata for the conversation")


class ChatHistory(BaseModel):
    """Response model for chat history."""
    conversation_id: str = Field(..., description="The conversation ID")
    messages: List[MessageModel] = Field(..., description="List of messages in chronological order")


class UserProfile(BaseModel):
    """Model for user profile information."""
    user_id: str = Field(..., description="The user's unique identifier")
    email: str = Field(..., description="The user's email address")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""
    user: UserProfile
    access_token: str
    refresh_token: str


class ConversationListResponse(BaseModel):
    """Response model for listing conversations."""
    conversations: List[ConversationModel] = Field(..., description="List of user conversations")
    total: int = Field(..., description="Total number of conversations")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of conversations per page")


# Legacy models for backward compatibility
class AgentState(BaseModel):
    """State model for LangGraph agent (legacy compatibility)."""
    messages: Sequence[BaseMessage]
    
    class Config:
        arbitrary_types_allowed = True
