from typing import List, Optional
from config import get_supabase_client
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import uuid


class ConversationService:
    def __init__(self, db=None):
        # db kept for compatibility; Supabase will be used instead
        self.db = db
        self.sb = get_supabase_client()

    async def create_conversation(self, user_id: uuid.UUID, title: str, category: Optional[str] = None):
        resp = self.sb.table("conversations").insert({
            "user_id": str(user_id),
            "title": title,
        }).select("*").execute()
        return resp.data[0]

    async def get_user_conversations(self, user_id: uuid.UUID):
        resp = self.sb.table("conversations").select("*")\
            .eq("user_id", str(user_id)).order("updated_at", desc=True).execute()
        return resp.data

    async def get_conversation_by_id(self, conversation_id: str, user_id: uuid.UUID):
        convo = self.sb.table("conversations").select("*")\
            .eq("id", conversation_id).single().execute().data
        if not convo or convo.get("user_id") != str(user_id):
            return None
        msgs = self.sb.table("messages").select("*")\
            .eq("conversation_id", conversation_id).order("created_at").execute().data
        convo["messages"] = msgs
        return convo

    async def delete_conversation(self, conversation_id: str, user_id: uuid.UUID) -> bool:
        self.sb.table("conversations").delete()\
            .eq("id", conversation_id).eq("user_id", str(user_id)).execute()
        return True

    async def update_conversation(self, conversation_id: str, user_id: uuid.UUID, title: Optional[str] = None, category: Optional[str] = None):
        update = {}
        if title is not None:
            update["title"] = title
        if category is not None:
            update["category"] = category
        if not update:
            return await self.get_conversation_by_id(conversation_id, user_id)
        resp = self.sb.table("conversations").update(update)\
            .eq("id", conversation_id).eq("user_id", str(user_id)).select("*").execute()
        return resp.data[0] if resp.data else None

    async def add_message_to_conversation(self, conversation_id: str, role: str, content: str, tool_name: Optional[str] = None, tool_call_id: Optional[str] = None):
        resp = self.sb.table("messages").insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
        }).select("*").execute()
        return resp.data[0]

    async def get_conversation_messages(self, conversation_id: str):
        resp = self.sb.table("messages").select("*")\
            .eq("conversation_id", conversation_id).order("created_at").execute()
        return resp.data

    async def messages_to_langchain_format(self, messages: List[dict]) -> List[BaseMessage]:
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        return langchain_messages

    async def save_langchain_messages_to_conversation(self, conversation_id: str, messages: List[BaseMessage]):
        saved = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"; content = msg.content
            elif isinstance(msg, AIMessage):
                role = "assistant"; content = msg.content
            else:
                continue
            saved.append(await self.add_message_to_conversation(conversation_id, role, content))
        return saved
