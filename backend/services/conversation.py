from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from models.database import Conversation, Message, User
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import uuid


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(self, user_id: uuid.UUID, title: str, category: Optional[str] = None) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(user_id=user_id, title=title)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_user_conversations(self, user_id: uuid.UUID) -> List[Conversation]:
        """Get all conversations for a user."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
        )
        return result.scalars().all()

    async def get_conversation_by_id(self, conversation_id: int, user_id: uuid.UUID) -> Optional[Conversation]:
        """Get a conversation by ID, ensuring it belongs to the user."""
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete_conversation(self, conversation_id: int, user_id: uuid.UUID) -> bool:
        """Delete a conversation, ensuring it belongs to the user."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        
        if conversation:
            await self.db.delete(conversation)
            await self.db.commit()
            return True
        return False

    async def update_conversation(
        self, 
        conversation_id: int, 
        user_id: uuid.UUID, 
        title: Optional[str] = None, 
        category: Optional[str] = None
    ) -> Optional[Conversation]:
        """Update a conversation's title or category."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        
        if conversation:
            if title is not None:
                conversation.title = title
            if category is not None:
                conversation.category = category
            
            await self.db.commit()
            await self.db.refresh(conversation)
            return conversation
        return None

    async def add_message_to_conversation(
        self, 
        conversation_id: int, 
        role: str, 
        content: str,
        tool_name: Optional[str] = None,
        tool_call_id: Optional[str] = None
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_name=tool_name,
            tool_call_id=tool_call_id
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        """Get all messages for a conversation."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    async def messages_to_langchain_format(self, messages: List[Message]) -> List[BaseMessage]:
        """Convert database messages to LangChain message format."""
        langchain_messages = []
        
        for msg in messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "tool":
                langchain_messages.append(
                    ToolMessage(
                        content=msg.content,
                        name=msg.tool_name or "",
                        tool_call_id=msg.tool_call_id or ""
                    )
                )
        
        return langchain_messages

    async def save_langchain_messages_to_conversation(
        self, 
        conversation_id: int, 
        messages: List[BaseMessage]
    ) -> List[Message]:
        """Save LangChain messages to the database."""
        saved_messages = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
                content = msg.content
                tool_name = None
                tool_call_id = None
            elif isinstance(msg, AIMessage):
                role = "assistant"
                content = msg.content
                tool_name = None
                tool_call_id = None
            elif isinstance(msg, ToolMessage):
                role = "tool"
                content = msg.content
                tool_name = msg.name
                tool_call_id = msg.tool_call_id
            else:
                continue  # Skip unknown message types
            
            saved_message = await self.add_message_to_conversation(
                conversation_id=conversation_id,
                role=role,
                content=content,
                tool_name=tool_name,
                tool_call_id=tool_call_id
            )
            saved_messages.append(saved_message)
        
        return saved_messages
