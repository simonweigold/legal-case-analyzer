import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from schemas.conversation import ChatRequestWithConversation, ChatResponseWithConversation  # conversation models only
from auth.auth import current_active_user
from models.database import User
from database.database import get_async_session, async_session_maker
from services.conversation import ConversationService

router = APIRouter(prefix="/chat", tags=["chat"])

# Set up logger
logger = logging.getLogger(__name__)

# Initialize the language model (will be set by main.py)
model = None
tools_by_name = None
# Temporary flag to disable all LLM tool usage (simple answers only)
DISABLE_LLM_TOOLS = False  # Re-enabled for welcome tool usage


def set_model_and_tools(llm_model, tools_dict):
    """Set the model and tools from main.py to avoid circular imports."""
    global model, tools_by_name
    model = llm_model
    tools_by_name = tools_dict


def create_model_with_selected_tools(selected_tools=None):
    """Create a model instance with only the selected tools."""
    from langchain_openai import ChatOpenAI
    from config import settings
    
    # If tools are globally disabled, always return a fresh model without tools
    if DISABLE_LLM_TOOLS:
        return ChatOpenAI(model=settings.MODEL_NAME, streaming=settings.STREAMING)
    
    if selected_tools is None:
        # Return the default model with all tools
        return model
    
    # Filter tools by name
    filtered_tools = []
    for tool_name in selected_tools:
        if tool_name in tools_by_name:
            filtered_tools.append(tools_by_name[tool_name])
    
    # If no valid tools selected, return model with no tools
    if not filtered_tools:
        return ChatOpenAI(model=settings.MODEL_NAME, streaming=settings.STREAMING)
    
    # Create new model instance with selected tools
    new_model = ChatOpenAI(model=settings.MODEL_NAME, streaming=settings.STREAMING)
    return new_model.bind_tools(filtered_tools)


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
    logger.info(f"Regular chat request from user {user.id}, conversation_id: {request.conversation_id}")
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
    user: User = Depends(current_active_user)
):
    """
    Send a message to the AI assistant with streaming response and conversation management.
    """
    async def generate_stream():
        logger.info(f"Starting stream for user {user.id}, conversation_id: {request.conversation_id}")
        # Create a new session specifically for this streaming operation
        async with async_session_maker() as db:
            try:
                logger.info("Database session created successfully")
                conversation_service = ConversationService(db)
            
                # Handle conversation creation or retrieval
                if request.conversation_id is None:
                    # Create new conversation
                    logger.info("Creating new conversation")
                    title = request.conversation_title or f"Chat {request.message[:30]}..."
                    conversation = await conversation_service.create_conversation(
                        user_id=user.id, 
                        title=title
                    )
                    conversation_id = conversation.id
                    logger.info(f"Created conversation with ID: {conversation_id}")
                else:
                    # Verify conversation belongs to user
                    logger.info(f"Retrieving existing conversation: {request.conversation_id}")
                    conversation = await conversation_service.get_conversation_by_id(
                        request.conversation_id, user.id
                    )
                    if not conversation:
                        logger.warning(f"Conversation {request.conversation_id} not found for user {user.id}")
                        yield f"data: {json.dumps({'error': 'Conversation not found', 'done': True, 'type': 'error'})}\n\n"
                        return
                    conversation_id = conversation.id
                    logger.info(f"Using existing conversation ID: {conversation_id}")

                # Get existing messages from conversation
                logger.info(f"Loading messages for conversation {conversation_id}")
                db_messages = await conversation_service.get_conversation_messages(conversation_id)
                logger.info(f"Loaded {len(db_messages)} existing messages")
                langchain_messages = await conversation_service.messages_to_langchain_format(db_messages)
                
                # Add new user message
                logger.info(f"Adding user message to conversation {conversation_id}")
                await conversation_service.add_message_to_conversation(
                    conversation_id=conversation_id,
                    role="user",
                    content=request.message
                )
                langchain_messages.append(HumanMessage(content=request.message))

                # System prompt for legal case analysis context
                system_prompt = SystemMessage(
                    "You are a helpful AI legal assistant. You can analyze legal cases and use tools for said tasks when explicitly asked.\n\n"
                    "CRITICAL INSTRUCTIONS:\n"
                    "- If a user just says 'hello', 'hi', or asks general legal questions, answer using the welcome tool\n"
                    "Be helpful and conversational. Provide legal information from your knowledge and using tools."
                )
                
                # Prepare messages for streaming
                messages_for_llm = [system_prompt] + langchain_messages
                logger.info(f"Prepared {len(messages_for_llm)} messages for LLM")
                
                # Check if model is available
                if model is None:
                    logger.error("Model is not initialized!")
                    yield f"data: {json.dumps({'error': 'Model not available', 'done': True, 'type': 'error'})}\n\n"
                    return
                
                # Create model with selected tools if specified
                active_model = create_model_with_selected_tools(request.tools)
                logger.info(f"Using model with tools: {request.tools if request.tools else 'all tools'}")
                
                # Get available tools for this request
                available_tools = tools_by_name
                if request.tools:
                    available_tools = {name: tool for name, tool in tools_by_name.items() if name in request.tools}
                    logger.info(f"Filtered to {len(available_tools)} tools: {list(available_tools.keys())}")
                
                # First non-stream invocation to check for tool calls
                logger.info("Invoking model to detect potential tool calls...")
                initial_response = active_model.invoke(messages_for_llm)

                tool_messages = []
                if hasattr(initial_response, 'tool_calls') and initial_response.tool_calls:
                    logger.info(f"Detected {len(initial_response.tool_calls)} tool calls: {[tc['name'] for tc in initial_response.tool_calls]}")
                    for tc in initial_response.tool_calls:
                        tool_name = tc.get('name')
                        tool_args = tc.get('args', {})
                        tool_id = tc.get('id')
                        if tool_name in available_tools:
                            try:
                                result = available_tools[tool_name].invoke(tool_args)
                                result_str = json.dumps(result) if not isinstance(result, str) else result
                                tool_msg = ToolMessage(content=result_str, name=tool_name, tool_call_id=tool_id)
                                tool_messages.append(tool_msg)
                                yield f"data: {json.dumps({'type': 'tool', 'content': result_str, 'tool_name': tool_name, 'conversation_id': conversation_id})}\n\n"
                                logger.info(f"Tool {tool_name} executed successfully")
                            except Exception as te:
                                err_content = f"Tool {tool_name} error: {str(te)}"
                                yield f"data: {json.dumps({'type': 'tool_error', 'content': err_content, 'tool_name': tool_name, 'conversation_id': conversation_id})}\n\n"
                                logger.error(err_content)
                        else:
                            logger.warning(f"Tool {tool_name} not available")

                # Prepare final messages for second pass:
                # OpenAI requires: assistant message with tool_calls -> tool messages -> follow-up assistant.
                if getattr(initial_response, 'tool_calls', []):
                    # Always include the assistant tool-call message first, then tool outputs.
                    final_messages_for_llm = messages_for_llm + [initial_response] + tool_messages
                else:
                    # No tools invoked; just append assistant response.
                    final_messages_for_llm = messages_for_llm + [initial_response]

                # Stream final response token-by-token
                accumulated_content = ""
                logger.info("Starting final streaming after tool execution (second assistant turn)...")
                async for chunk in active_model.astream(final_messages_for_llm):
                    if hasattr(chunk, 'content') and chunk.content:
                        accumulated_content += chunk.content
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.content, 'conversation_id': conversation_id})}\n\n"

                # Save final response
                logger.info(f"Final streaming completed. Content length: {len(accumulated_content)}")
                if accumulated_content:
                    await conversation_service.add_message_to_conversation(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=accumulated_content
                    )
                else:
                    logger.warning("No content accumulated in final streaming phase")

                yield f"data: {json.dumps({'type': 'complete', 'data': {'response': accumulated_content, 'conversation_id': conversation_id, 'message_id': None}})}\n\n"

            except Exception as e:
                # Send error in streaming format and ensure proper cleanup
                logger.error(f"Error in streaming: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'error': f'Error processing request: {str(e)}', 'done': True, 'type': 'error'})}\n\n"
            finally:
                # Session is automatically closed by the context manager
                logger.info("Streaming completed, session will be closed")
                pass

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


# Conversation Management Endpoints
@router.get("/conversations")
async def get_conversations(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all conversations for the current user.
    """
    try:
        conversation_service = ConversationService(db)
        conversations = await conversation_service.get_user_conversations(user.id)
        
        # Convert to response format
        conversation_responses = []
        for conv in conversations:
            # Get message count and last message
            messages = await conversation_service.get_conversation_messages(conv.id)
            last_message = messages[-1].content if messages else ""
            
            conversation_responses.append({
                "id": str(conv.id),
                "user_id": str(conv.user_id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "category": getattr(conv, 'category', None),
                "is_active": True,
                "messageCount": len(messages),
                "lastMessage": last_message[:100] + "..." if len(last_message) > 100 else last_message,
                "lastUpdated": conv.updated_at.isoformat()
            })
        
        return conversation_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific conversation by ID.
    """
    try:
        conversation_service = ConversationService(db)
        conversation = await conversation_service.get_conversation_by_id(conversation_id, user.id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "id": str(conversation.id),
            "user_id": str(conversation.user_id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "category": getattr(conversation, 'category', None),
            "is_active": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all messages for a specific conversation.
    """
    try:
        conversation_service = ConversationService(db)
        
        # Verify conversation belongs to user
        conversation = await conversation_service.get_conversation_by_id(conversation_id, user.id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await conversation_service.get_conversation_messages(conversation_id)
        
        # Convert to response format
        message_responses = []
        for msg in messages:
            message_responses.append({
                "id": str(msg.id),
                "conversation_id": str(msg.conversation_id),
                "content": msg.content,
                "role": msg.role,
                "timestamp": msg.created_at.isoformat(),
                "metadata": {
                    "tool_name": msg.tool_name,
                    "tool_call_id": msg.tool_call_id
                } if msg.tool_name else None
            })
        
        return message_responses
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")


@router.patch("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: int,
    title: Optional[str] = None,
    category: Optional[str] = None,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update conversation title or category.
    """
    try:
        conversation_service = ConversationService(db)
        
        # Verify conversation belongs to user
        conversation = await conversation_service.get_conversation_by_id(conversation_id, user.id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update conversation
        updated_conversation = await conversation_service.update_conversation(
            conversation_id, user.id, title=title, category=category
        )
        
        return {
            "id": str(updated_conversation.id),
            "user_id": str(updated_conversation.user_id),
            "title": updated_conversation.title,
            "created_at": updated_conversation.created_at.isoformat(),
            "updated_at": updated_conversation.updated_at.isoformat(),
            "category": getattr(updated_conversation, 'category', None),
            "is_active": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating conversation: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete a conversation and all its messages.
    """
    try:
        conversation_service = ConversationService(db)
        
        # Verify conversation belongs to user
        conversation = await conversation_service.get_conversation_by_id(conversation_id, user.id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete conversation (this should cascade to messages)
        await conversation_service.delete_conversation(conversation_id, user.id)
        
        return {"message": f"Conversation {conversation_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")


@router.post("/conversations")
async def create_conversation(
    title: str,
    category: Optional[str] = None,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new conversation.
    """
    try:
        conversation_service = ConversationService(db)
        conversation = await conversation_service.create_conversation(
            user_id=user.id, 
            title=title,
            category=category
        )
        
        return {
            "id": str(conversation.id),
            "user_id": str(conversation.user_id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "category": getattr(conversation, 'category', None),
            "is_active": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")
