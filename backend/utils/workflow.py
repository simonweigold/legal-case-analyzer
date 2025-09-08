from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from typing import Annotated, Sequence, Dict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# Agent State Definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def tool_node(state: AgentState, tools_by_name):
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

def call_model(state: AgentState, config: RunnableConfig, model):
    system_prompt = SystemMessage(
        "You are a helpful AI legal assistant specialized in analyzing legal cases. "
        "You can help with case analysis, finding precedents, and providing legal insights. "
        "Always provide thorough and professional responses while noting that your advice "
        "should not replace consultation with qualified legal professionals."
    )
    response = model.invoke([system_prompt] + state["messages"], config)
    return {"messages": [response]}
