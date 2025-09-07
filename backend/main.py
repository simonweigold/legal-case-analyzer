"""
Legal Case Analyzer FastAPI Backend with Supabase Integration
"""
import os
from dotenv import find_dotenv, load_dotenv
import json
import asyncio
from typing import Annotated, Sequence, TypedDict, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv(find_dotenv())

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END

# Supabase integration imports
from auth import AuthUser, get_current_user, get_optional_user
from models import (
    ChatRequest, ChatResponse, StreamChatRequest, ChatHistory,
    ConversationModel, CreateConversationRequest, UpdateConversationRequest,
    ConversationListResponse, MessageModel
)
from supabase_service import conversation_service, message_service


# Legacy models for backward compatibility
class LegacyChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class LegacyChatResponse(BaseModel):
    response: str
    session_id: str


class LegacyStreamChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class LegacyChatHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]


# Agent State Definition
class AgentState(TypedDict):
    """The state of the agent."""
    # add_messages is a reducer
    # See https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Initialize the language model
model = ChatOpenAI(model="gpt-4o-mini", streaming=True)


# Define tools
@tool
def analyze_legal_case(case_details: str):
    """Analyze legal case details and provide insights."""
    # This is a placeholder for actual legal case analysis
    # In a real implementation, this would connect to legal databases or analysis tools
    return f"Legal case analysis for: {case_details}\n\nKey considerations:\n- Precedent review needed\n- Statutory compliance check required\n- Risk assessment: Medium"


@tool
def search_legal_precedents(query: str):
    """Search for legal precedents related to a query."""
    # Placeholder for legal precedent search
    return f"Found relevant precedents for '{query}':\n1. Case A vs B (2020) - Similar circumstances\n2. Case C vs D (2019) - Related legal principle\n3. Case E vs F (2018) - Applicable statute interpretation"


# Setup tools
tools = [analyze_legal_case, search_legal_precedents]
model = model.bind_tools(tools)
tools_by_name = {tool.name: tool for tool in tools}


# In-memory session storage (in production, use a proper database)
session_storage: Dict[str, List[BaseMessage]] = {}


# Define tool node
def tool_node(state: AgentState):
    outputs = []
    for tool_call in state["messages"][-1].tool_calls:
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            ToolMessage(
                content=json.dumps(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}


# Define the node that calls the model
def call_model(state: AgentState, config: RunnableConfig):
    # System prompt for legal case analysis context
    system_prompt = SystemMessage(
        "You are a helpful AI legal assistant specialized in analyzing legal cases. "
        "You can help with case analysis, finding precedents, and providing legal insights. "
        "Always provide thorough and professional responses while noting that your advice "
        "should not replace consultation with qualified legal professionals."
    )
    response = model.invoke([system_prompt] + state["messages"], config)
    return {"messages": [response]}


# Define the conditional edge
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


# Create the workflow graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)

workflow.add_edge("tools", "agent")

# Compile the graph
graph = workflow.compile()


# Initialize FastAPI app
app = FastAPI(title="Legal Case Analyzer API", version="1.0.0")

# CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development: allow all; tighten for production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Legal Case Analyzer API", "version": "1.0.0", "supabase": True}


# ========================================
# Supabase-enabled Authentication Endpoints
# ========================================

@app.get("/auth/user", response_model=MessageModel)
async def get_user_profile(current_user: AuthUser = Depends(get_current_user)):
    """Get the current user's profile information."""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "metadata": current_user.metadata
    }


# ========================================
# Supabase-enabled Conversation Management
# ========================================

@app.post("/conversations", response_model=ConversationModel)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new conversation for the authenticated user."""
    try:
        conversation = await conversation_service.create_conversation(
            user=current_user,
            title=request.title,
            metadata=request.metadata
        )
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@app.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    page: int = 1,
    page_size: int = 20,
    current_user: AuthUser = Depends(get_current_user)
):
    """List all conversations for the authenticated user."""
    try:
        conversations = await conversation_service.get_conversations(
            user=current_user,
            page=page,
            page_size=page_size
        )
        return ConversationListResponse(
            conversations=conversations,
            total=len(conversations),  # TODO: Implement proper count
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")


@app.get("/conversations/{conversation_id}", response_model=ConversationModel)
async def get_conversation(
    conversation_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get a specific conversation."""
    try:
        conversation = await conversation_service.get_conversation(conversation_id, current_user)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@app.put("/conversations/{conversation_id}", response_model=ConversationModel)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update a conversation."""
    try:
        conversation = await conversation_service.update_conversation(
            conversation_id=conversation_id,
            user=current_user,
            title=request.title,
            metadata=request.metadata
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update conversation: {str(e)}")


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Delete a conversation and all its messages."""
    try:
        success = await conversation_service.delete_conversation(conversation_id, current_user)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")


# ========================================
# Supabase-enabled Chat Endpoints
# ========================================

@app.post("/conversations/{conversation_id}/chat", response_model=ChatResponse)
async def chat_with_conversation(
    conversation_id: str,
    request: ChatRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Send a message to an existing conversation."""
    try:
        # Verify the conversation exists and belongs to the user
        conversation = await conversation_service.get_conversation(conversation_id, current_user)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get conversation history
        messages_history = await message_service.get_messages(conversation_id)
        
        # Convert to LangChain messages
        langchain_messages = []
        for msg in messages_history:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))

        # Add the new user message
        user_message = HumanMessage(content=request.message)
        langchain_messages.append(user_message)

        # Save user message to database
        await message_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        # Prepare input for the graph
        inputs = {"messages": langchain_messages}

        # Run the graph and collect the final response
        final_state = None
        for chunk in graph.stream(inputs, stream_mode="values"):
            final_state = chunk

        if final_state and final_state["messages"]:
            # Get the last AI message
            last_message = final_state["messages"][-1]
            if isinstance(last_message, AIMessage):
                ai_response = last_message.content
                
                # Save AI response to database
                await message_service.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=ai_response
                )
                
                return ChatResponse(response=ai_response, conversation_id=conversation_id)
            
        # Save fallback response
        fallback_response = "I apologize, but I couldn't generate a proper response. Please try again."
        await message_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=fallback_response
        )
        
        return ChatResponse(response=fallback_response, conversation_id=conversation_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/conversations/{conversation_id}/messages", response_model=List[MessageModel])
async def get_conversation_messages(
    conversation_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all messages for a conversation."""
    try:
        # Verify the conversation exists and belongs to the user
        conversation = await conversation_service.get_conversation(conversation_id, current_user)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = await message_service.get_messages(conversation_id)
        return messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


# ========================================
# Legacy Endpoints (for backward compatibility)
# ========================================

@app.post("/chat", response_model=LegacyChatResponse)
async def chat_endpoint(request: LegacyChatRequest):
    """
    LEGACY: Send a message to the AI assistant and receive a response.
    Maintains conversation context per session.
    """
    try:
        session_id = request.session_id
        user_message = request.message

        # Get or initialize session history
        if session_id not in session_storage:
            session_storage[session_id] = []

        # Add user message to session history
        session_storage[session_id].append(HumanMessage(content=user_message))

        # Prepare input for the graph with session context
        inputs = {"messages": session_storage[session_id]}

        # Run the graph and collect the final response
        final_state = None
        for chunk in graph.stream(inputs, stream_mode="values"):
            final_state = chunk

        if final_state and final_state["messages"]:
            # Get the last AI message
            last_message = final_state["messages"][-1]
            if isinstance(last_message, AIMessage):
                ai_response = last_message.content
                
                # Update session storage with the complete conversation
                session_storage[session_id] = final_state["messages"]
                
                return LegacyChatResponse(response=ai_response, session_id=session_id)
            
        return LegacyChatResponse(response="I apologize, but I couldn't generate a proper response. Please try again.", session_id=session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/chat/stream")
async def stream_chat_endpoint(request: LegacyStreamChatRequest):
    """
    Send a message to the AI assistant and receive a streaming response.
    Maintains conversation context per session.
    """
    async def generate_stream():
        try:
            session_id = request.session_id
            user_message = request.message

            # Get or initialize session history
            if session_id not in session_storage:
                session_storage[session_id] = []

            # Add user message to session history
            session_storage[session_id].append(HumanMessage(content=user_message))

            # System prompt for legal case analysis context
            system_prompt = SystemMessage(
                "You are a helpful AI legal assistant specialized in analyzing legal cases. "
                "You can help with case analysis, finding precedents, and providing legal insights. "
                "Always provide thorough and professional responses while noting that your advice "
                "should not replace consultation with qualified legal professionals."
            )
            
            # Prepare messages for streaming
            messages_for_llm = [system_prompt] + session_storage[session_id]
            
            # Stream directly from the model for token-by-token streaming
            accumulated_content = ""
            
            async for chunk in model.astream(messages_for_llm):
                if hasattr(chunk, 'content') and chunk.content:
                    accumulated_content += chunk.content
                    yield f"data: {json.dumps({'content': chunk.content, 'session_id': session_id, 'done': False, 'type': 'token'})}\n\n"
                
                # Handle tool calls if present
                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    for tool_call in chunk.tool_calls:
                        tool_name = tool_call["name"]
                        tool_message = f"Calling tool: {tool_name}"
                        yield f"data: {json.dumps({'content': tool_message, 'session_id': session_id, 'done': False, 'type': 'tool'})}\n\n"
                        
                        # Execute the tool
                        if tool_name in tools_by_name:
                            tool_result = tools_by_name[tool_name].invoke(tool_call["args"])
                            
                            # Add tool message to session
                            tool_message = ToolMessage(
                                content=json.dumps(tool_result),
                                name=tool_name,
                                tool_call_id=tool_call["id"],
                            )
                            session_storage[session_id].append(AIMessage(content="", tool_calls=[tool_call]))
                            session_storage[session_id].append(tool_message)
                            
                            result_message = f"Tool result: {tool_result}"
                            yield f"data: {json.dumps({'content': result_message, 'session_id': session_id, 'done': False, 'type': 'tool_result'})}\n\n"
                            
                            # Continue streaming with tool result
                            messages_for_llm = [system_prompt] + session_storage[session_id]
                            async for follow_chunk in model.astream(messages_for_llm):
                                if hasattr(follow_chunk, 'content') and follow_chunk.content:
                                    accumulated_content += follow_chunk.content
                                    yield f"data: {json.dumps({'content': follow_chunk.content, 'session_id': session_id, 'done': False, 'type': 'token'})}\n\n"

            # Add the final AI response to session storage
            if accumulated_content:
                session_storage[session_id].append(AIMessage(content=accumulated_content))

            # Send completion signal
            yield f"data: {json.dumps({'content': '', 'session_id': session_id, 'done': True, 'type': 'done'})}\n\n"

        except Exception as e:
            # Send error in streaming format
            yield f"data: {json.dumps({'error': f'Error processing request: {str(e)}', 'session_id': request.session_id, 'done': True, 'type': 'error'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@app.get("/chat/history/{session_id}", response_model=LegacyChatHistory)
async def get_chat_history(session_id: str):
    """
    LEGACY: Retrieve chat history for a specific session.
    """
    if session_id not in session_storage:
        return LegacyChatHistory(session_id=session_id, messages=[])
    
    messages = []
    for msg in session_storage[session_id]:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, ToolMessage):
            messages.append({"role": "tool", "content": f"Tool: {msg.name} - {msg.content}"})
    
    return LegacyChatHistory(session_id=session_id, messages=messages)


@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a specific session.
    """
    if session_id in session_storage:
        del session_storage[session_id]
        return {"message": f"Chat history cleared for session {session_id}"}
    else:
        return {"message": f"No chat history found for session {session_id}"}


@app.get("/chat/sessions")
async def list_sessions():
    """
    List all active chat sessions.
    """
    return {"sessions": list(session_storage.keys()), "count": len(session_storage)}


if __name__ == "__main__":
    print("Starting Legal Case Analyzer API...")
    print("API will be available at: http://localhost:1")
    print("API documentation at: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)
