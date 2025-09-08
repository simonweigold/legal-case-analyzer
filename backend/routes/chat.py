import json
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from schemas.chat import ChatRequest, ChatResponse, StreamChatRequest, ChatHistory
from services.session import (
    get_session_messages, 
    update_session_messages, 
    clear_session, 
    get_all_sessions
)
from services.tools import get_tools_by_name

router = APIRouter()

# Initialize the language model
model = ChatOpenAI(model="gpt-4o-mini", streaming=True)
tools_by_name = get_tools_by_name()


def get_graph(request: Request):
    """Dependency to get the graph from app state."""
    return request.app.state.graph


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, graph=Depends(get_graph)):
    """
    Send a message to the AI assistant and receive a response.
    Maintains conversation context per session.
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


@router.post("/chat/stream")
async def stream_chat_endpoint(request: StreamChatRequest):
    """
    Send a message to the AI assistant and receive a streaming response.
    Maintains conversation context per session.
    """
    async def generate_stream():
        try:
            session_id = request.session_id
            user_message = request.message

            # Get session messages
            session_messages = get_session_messages(session_id)

            # Add user message to session history
            session_messages.append(HumanMessage(content=user_message))

            # System prompt for legal case analysis context
            system_prompt = SystemMessage(
                "You are a helpful AI legal assistant specialized in analyzing legal cases. "
                "You can help with case analysis, finding precedents, and providing legal insights. "
                "Always provide thorough and professional responses while noting that your advice "
                "should not replace consultation with qualified legal professionals."
            )
            
            # Prepare messages for streaming
            messages_for_llm = [system_prompt] + session_messages
            
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
                            session_messages.append(AIMessage(content="", tool_calls=[tool_call]))
                            session_messages.append(tool_message)
                            
                            result_message = f"Tool result: {tool_result}"
                            yield f"data: {json.dumps({'content': result_message, 'session_id': session_id, 'done': False, 'type': 'tool_result'})}\n\n"
                            
                            # Continue streaming with tool result
                            messages_for_llm = [system_prompt] + session_messages
                            async for follow_chunk in model.astream(messages_for_llm):
                                if hasattr(follow_chunk, 'content') and follow_chunk.content:
                                    accumulated_content += follow_chunk.content
                                    yield f"data: {json.dumps({'content': follow_chunk.content, 'session_id': session_id, 'done': False, 'type': 'token'})}\n\n"

            # Add the final AI response to session storage
            if accumulated_content:
                session_messages.append(AIMessage(content=accumulated_content))
                update_session_messages(session_id, session_messages)

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


@router.get("/chat/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a specific session.
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


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a specific session.
    """
    clear_session(session_id)
    return {"message": f"Chat history cleared for session {session_id}"}


@router.get("/chat/sessions")
async def list_sessions():
    """
    List all active chat sessions.
    """
    sessions = get_all_sessions()
    return {"sessions": sessions, "count": len(sessions)}
