import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from schemas.chat import ChatRequest, ChatResponse, StreamChatRequest, ChatHistory
from schemas.conversation import ChatRequestWithConversation, ChatResponseWithConversation
from auth import current_active_user
from models.database import User
from database import get_async_session
from services.conversation import ConversationService

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize the language model (will be set by main.py)
model = None
tools_by_name = None


def set_model_and_tools(llm_model, tools_dict):
    """Set the model and tools from main.py to avoid circular imports."""
    global model, tools_by_name
    model = llm_model
    tools_by_name = tools_dict


def get_graph(request: Request):
    """Dependency to get the graph from app state."""
    return request.app.state.graph


@router.post("/", response_model=ChatResponseWithConversation)
async def chat_with_conversation(
    request: ChatRequestWithConversation,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
    graph=Depends(get_graph)
):
    """
    Send a message to the AI assistant with conversation management.
    Creates a new conversation if conversation_id is not provided.
    """
    try:
        conversation_service = ConversationService(db)
        
        # Handle conversation creation or retrieval
        if request.conversation_id is None:
            # Create new conversation
            title = request.conversation_title or f"Chat {request.message[:30]}..."
            conversation = await conversation_service.create_conversation(
                user_id=user.id, 
                title=title
            )
            conversation_id = conversation.id
        else:
            # Verify conversation belongs to user
            conversation = await conversation_service.get_conversation_by_id(
                request.conversation_id, user.id
            )
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            conversation_id = conversation.id

        # Get existing messages from conversation
        db_messages = await conversation_service.get_conversation_messages(conversation_id)
        langchain_messages = await conversation_service.messages_to_langchain_format(db_messages)
        
        # Add new user message
        await conversation_service.add_message_to_conversation(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        langchain_messages.append(HumanMessage(content=request.message))

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
                await conversation_service.add_message_to_conversation(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=ai_response
                )
                
                # Get conversation details for response
                conversation = await conversation_service.get_conversation_by_id(
                    conversation_id, user.id
                )
                
                return ChatResponseWithConversation(
                    response=ai_response, 
                    conversation_id=conversation_id,
                    conversation_title=conversation.title
                )
            
        raise HTTPException(status_code=500, detail="Could not generate response")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/stream")
async def stream_chat_with_conversation(
    request: ChatRequestWithConversation,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Send a message to the AI assistant with streaming response and conversation management.
    """
    async def generate_stream():
        try:
            conversation_service = ConversationService(db)
            
            # Handle conversation creation or retrieval
            if request.conversation_id is None:
                # Create new conversation
                title = request.conversation_title or f"Chat {request.message[:30]}..."
                conversation = await conversation_service.create_conversation(
                    user_id=user.id, 
                    title=title
                )
                conversation_id = conversation.id
            else:
                # Verify conversation belongs to user
                conversation = await conversation_service.get_conversation_by_id(
                    request.conversation_id, user.id
                )
                if not conversation:
                    yield f"data: {json.dumps({'error': 'Conversation not found', 'done': True, 'type': 'error'})}\n\n"
                    return
                conversation_id = conversation.id

            # Get existing messages from conversation
            db_messages = await conversation_service.get_conversation_messages(conversation_id)
            langchain_messages = await conversation_service.messages_to_langchain_format(db_messages)
            
            # Add new user message
            await conversation_service.add_message_to_conversation(
                conversation_id=conversation_id,
                role="user",
                content=request.message
            )
            langchain_messages.append(HumanMessage(content=request.message))

            # System prompt for legal case analysis context
            system_prompt = SystemMessage(
                "You are a helpful AI legal assistant specialized in analyzing legal cases. "
                "You can help with case analysis, finding precedents, and providing legal insights. "
                "Always provide thorough and professional responses while noting that your advice "
                "should not replace consultation with qualified legal professionals."
            )
            
            # Prepare messages for streaming
            messages_for_llm = [system_prompt] + langchain_messages
            
            # Stream directly from the model for token-by-token streaming
            accumulated_content = ""
            
            async for chunk in model.astream(messages_for_llm):
                if hasattr(chunk, 'content') and chunk.content:
                    accumulated_content += chunk.content
                    yield f"data: {json.dumps({'content': chunk.content, 'conversation_id': conversation_id, 'done': False, 'type': 'token'})}\n\n"
                
                # Handle tool calls if present
                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    for tool_call in chunk.tool_calls:
                        tool_name = tool_call["name"]
                        tool_message = f"Calling tool: {tool_name}"
                        yield f"data: {json.dumps({'content': tool_message, 'conversation_id': conversation_id, 'done': False, 'type': 'tool'})}\n\n"
                        
                        # Execute the tool
                        if tool_name in tools_by_name:
                            tool_result = tools_by_name[tool_name].invoke(tool_call["args"])
                            
                            # Save tool messages to database
                            await conversation_service.add_message_to_conversation(
                                conversation_id=conversation_id,
                                role="tool",
                                content=json.dumps(tool_result),
                                tool_name=tool_name,
                                tool_call_id=tool_call["id"]
                            )
                            
                            result_message = f"Tool result: {tool_result}"
                            yield f"data: {json.dumps({'content': result_message, 'conversation_id': conversation_id, 'done': False, 'type': 'tool_result'})}\n\n"

            # Save the final AI response to database
            if accumulated_content:
                await conversation_service.add_message_to_conversation(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=accumulated_content
                )

            # Send completion signal
            yield f"data: {json.dumps({'content': '', 'conversation_id': conversation_id, 'done': True, 'type': 'done'})}\n\n"

        except Exception as e:
            # Send error in streaming format
            yield f"data: {json.dumps({'error': f'Error processing request: {str(e)}', 'done': True, 'type': 'error'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


# Legacy endpoints for backward compatibility (using in-memory sessions)
from services.session import (
    get_session_messages, 
    update_session_messages, 
    clear_session, 
    get_all_sessions
)


@router.post("/legacy", response_model=ChatResponse)
async def chat_endpoint_legacy(request: ChatRequest, graph=Depends(get_graph)):
    """
    Legacy chat endpoint using session-based storage (backward compatibility).
    """
    try:
        session_id = request.session_id
        user_message = request.message

        # Get session messages
        session_messages = get_session_messages(session_id)
        
        # Add user message to session history
        session_messages.append(HumanMessage(content=user_message))

        # Prepare input for the graph with session context
        inputs = {"messages": session_messages}

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
                update_session_messages(session_id, final_state["messages"])
                
                return ChatResponse(response=ai_response, session_id=session_id)
            
        return ChatResponse(response="I apologize, but I couldn't generate a proper response. Please try again.", session_id=session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history_legacy(session_id: str):
    """
    Legacy chat history endpoint (backward compatibility).
    """
    session_messages = get_session_messages(session_id)
    
    messages = []
    for msg in session_messages:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, ToolMessage):
            messages.append({"role": "tool", "content": f"Tool: {msg.name} - {msg.content}"})
    
    return ChatHistory(session_id=session_id, messages=messages)


@router.delete("/history/{session_id}")
async def clear_chat_history_legacy(session_id: str):
    """
    Legacy clear chat history endpoint (backward compatibility).
    """
    clear_session(session_id)
    return {"message": f"Chat history cleared for session {session_id}"}


@router.get("/sessions")
async def list_sessions_legacy():
    """
    Legacy list sessions endpoint (backward compatibility).
    """
    sessions = get_all_sessions()
    return {"sessions": sessions, "count": len(sessions)}
