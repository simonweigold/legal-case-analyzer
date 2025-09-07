"""
Service layer for Supabase database operations.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from supabase import Client
from supabase_config import get_supabase
from models import ConversationModel, MessageModel, ConversationWithMessages, UserProfile
from auth import AuthUser


class ConversationService:
    """Service for managing conversations in Supabase."""
    
    def __init__(self, supabase_client: Client = None):
        self.supabase = supabase_client or get_supabase()
    
    async def create_conversation(self, user: AuthUser, title: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> ConversationModel:
        """Create a new conversation for a user."""
        conversation_data = {
            "user_id": user.user_id,
            "title": title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "metadata": metadata or {}
        }
        
        result = self.supabase.table("conversations").insert(conversation_data).execute()
        
        if result.data:
            conversation = result.data[0]
            return ConversationModel(
                id=conversation["id"],
                user_id=conversation["user_id"],
                title=conversation["title"],
                metadata=conversation["metadata"],
                created_at=conversation["created_at"],
                updated_at=conversation["updated_at"]
            )
        
        raise Exception("Failed to create conversation")
    
    async def get_conversation(self, conversation_id: str, user: AuthUser) -> Optional[ConversationModel]:
        """Get a specific conversation by ID."""
        result = self.supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user.user_id).execute()
        
        if result.data:
            conversation = result.data[0]
            return ConversationModel(
                id=conversation["id"],
                user_id=conversation["user_id"],
                title=conversation["title"],
                metadata=conversation["metadata"],
                created_at=conversation["created_at"],
                updated_at=conversation["updated_at"]
            )
        
        return None
    
    async def get_conversations(self, user: AuthUser, page: int = 1, page_size: int = 20) -> List[ConversationModel]:
        """Get all conversations for a user with pagination."""
        offset = (page - 1) * page_size
        
        result = self.supabase.table("conversations")\
            .select("*")\
            .eq("user_id", user.user_id)\
            .order("updated_at", desc=True)\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        conversations = []
        if result.data:
            for conversation in result.data:
                conversations.append(ConversationModel(
                    id=conversation["id"],
                    user_id=conversation["user_id"],
                    title=conversation["title"],
                    metadata=conversation["metadata"],
                    created_at=conversation["created_at"],
                    updated_at=conversation["updated_at"]
                ))
        
        return conversations
    
    async def update_conversation(self, conversation_id: str, user: AuthUser, title: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[ConversationModel]:
        """Update a conversation."""
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if metadata is not None:
            update_data["metadata"] = metadata
        
        if not update_data:
            return await self.get_conversation(conversation_id, user)
        
        result = self.supabase.table("conversations")\
            .update(update_data)\
            .eq("id", conversation_id)\
            .eq("user_id", user.user_id)\
            .execute()
        
        if result.data:
            conversation = result.data[0]
            return ConversationModel(
                id=conversation["id"],
                user_id=conversation["user_id"],
                title=conversation["title"],
                metadata=conversation["metadata"],
                created_at=conversation["created_at"],
                updated_at=conversation["updated_at"]
            )
        
        return None
    
    async def delete_conversation(self, conversation_id: str, user: AuthUser) -> bool:
        """Delete a conversation and all its messages."""
        result = self.supabase.table("conversations")\
            .delete()\
            .eq("id", conversation_id)\
            .eq("user_id", user.user_id)\
            .execute()
        
        return len(result.data) > 0


class MessageService:
    """Service for managing messages in Supabase."""
    
    def __init__(self, supabase_client: Client = None):
        self.supabase = supabase_client or get_supabase()
    
    async def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> MessageModel:
        """Add a new message to a conversation."""
        message_data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        result = self.supabase.table("messages").insert(message_data).execute()
        
        if result.data:
            message = result.data[0]
            return MessageModel(
                id=message["id"],
                role=message["role"],
                content=message["content"],
                metadata=message["metadata"],
                created_at=message["created_at"]
            )
        
        raise Exception("Failed to add message")
    
    async def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[MessageModel]:
        """Get all messages for a conversation."""
        query = self.supabase.table("messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=False)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        
        messages = []
        if result.data:
            for message in result.data:
                messages.append(MessageModel(
                    id=message["id"],
                    role=message["role"],
                    content=message["content"],
                    metadata=message["metadata"],
                    created_at=message["created_at"]
                ))
        
        return messages
    
    async def get_conversation_with_messages(self, conversation_id: str, user: AuthUser) -> Optional[ConversationWithMessages]:
        """Get a conversation with all its messages."""
        conversation_service = ConversationService(self.supabase)
        conversation = await conversation_service.get_conversation(conversation_id, user)
        
        if not conversation:
            return None
        
        messages = await self.get_messages(conversation_id)
        
        return ConversationWithMessages(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            metadata=conversation.metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=messages
        )
    
    async def delete_messages(self, conversation_id: str) -> bool:
        """Delete all messages for a conversation."""
        result = self.supabase.table("messages")\
            .delete()\
            .eq("conversation_id", conversation_id)\
            .execute()
        
        return True  # Supabase doesn't return count for deletes


# Global service instances
conversation_service = ConversationService()
message_service = MessageService()
