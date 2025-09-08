from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.schemas.chat import ChatRequest, ChatResponse, StreamChatRequest, ChatHistory
from backend.utils.workflow import tool_node, call_model

router = APIRouter()

# In-memory session storage
session_storage = {}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Implementation here
    pass

@router.post("/chat/stream")
async def stream_chat_endpoint(request: StreamChatRequest):
    # Implementation here
    pass

@router.get("/chat/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(session_id: str):
    # Implementation here
    pass

@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    # Implementation here
    pass

@router.get("/chat/sessions")
async def list_sessions():
    # Implementation here
    pass
