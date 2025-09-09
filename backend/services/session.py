from typing import Dict, List
from langchain_core.messages import BaseMessage

# In-memory session storage (in production, use a proper database)
session_storage: Dict[str, List[BaseMessage]] = {}


def get_session_storage():
    """Get the session storage."""
    return session_storage


def get_session_messages(session_id: str) -> List[BaseMessage]:
    """Get messages for a specific session."""
    return session_storage.get(session_id, [])


def update_session_messages(session_id: str, messages: List[BaseMessage]):
    """Update messages for a specific session."""
    session_storage[session_id] = messages


def clear_session(session_id: str):
    """Clear messages for a specific session."""
    if session_id in session_storage:
        del session_storage[session_id]


def get_all_sessions():
    """Get all session IDs."""
    return list(session_storage.keys())
