import os
from dotenv import find_dotenv, load_dotenv
import json
import asyncio
from typing import Annotated, Sequence, TypedDict, Dict, List
from fastapi import FastAPI, HTTPException
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


# Pydantic models for API requests/responses
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


class StreamChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatHistory(BaseModel):
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
    return {"message": "Legal Case Analyzer API", "version": "1.0.0"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Send a message to the AI assistant and receive a response.
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
                
                return ChatResponse(response=ai_response, session_id=session_id)
            
        return ChatResponse(response="I apologize, but I couldn't generate a proper response. Please try again.", session_id=session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/chat/stream")
async def stream_chat_endpoint(request: StreamChatRequest):
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


@app.get("/chat/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a specific session.
    """
    if session_id not in session_storage:
        return ChatHistory(session_id=session_id, messages=[])
    
    messages = []
    for msg in session_storage[session_id]:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, ToolMessage):
            messages.append({"role": "tool", "content": f"Tool: {msg.name} - {msg.content}"})
    
    return ChatHistory(session_id=session_id, messages=messages)


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
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
