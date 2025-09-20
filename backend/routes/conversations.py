from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from auth.auth import current_active_user
from models.database import User
from database.database import get_async_session
from services.conversation import ConversationService
from schemas.conversation import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationWithMessages,
    MessageResponse
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new conversation for the authenticated user."""
    conversation_service = ConversationService(db)
    conversation = await conversation_service.create_conversation(
        user_id=user.id, 
        title=conversation_data.title
    )
    return conversation


@router.get("/", response_model=List[ConversationResponse])
async def get_user_conversations(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get all conversations for the authenticated user."""
    conversation_service = ConversationService(db)
    conversations = await conversation_service.get_user_conversations(user.id)
    return conversations


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation_with_messages(
    conversation_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get a specific conversation with all its messages."""
    conversation_service = ConversationService(db)
    conversation = await conversation_service.get_conversation_by_id(conversation_id, user.id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a conversation."""
    conversation_service = ConversationService(db)
    deleted = await conversation_service.delete_conversation(conversation_id, user.id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Conversation deleted successfully"}


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get all messages for a specific conversation."""
    conversation_service = ConversationService(db)
    
    # First verify the conversation belongs to the user
    conversation = await conversation_service.get_conversation_by_id(conversation_id, user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await conversation_service.get_conversation_messages(conversation_id)
    return messages
