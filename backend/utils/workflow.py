import json
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END


# Agent State Definition
class AgentState(TypedDict):
    """The state of the agent."""
    # add_messages is a reducer
    # See https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers
    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_tool_node(tools_by_name):
    """Create a tool node function with tools_by_name closure."""
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
    return tool_node


def create_call_model(model):
    """Create a call_model function with model closure."""
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
    return call_model


def should_continue(state: AgentState):
    """Define the conditional edge."""
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


def create_workflow(model, tools_by_name):
    """Create and compile the workflow graph."""
    tool_node = create_tool_node(tools_by_name)
    call_model = create_call_model(model)
    
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
    
    return workflow.compile()
