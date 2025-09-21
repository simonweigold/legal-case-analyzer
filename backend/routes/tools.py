from fastapi import APIRouter
from typing import List, Dict, Any
from tools.tools import get_tools
from tools.streaming_tools import get_streaming_tools

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/", response_model=List[Dict[str, Any]])
async def get_available_tools():
    """
    Get a list of all available legal analysis tools with their metadata.
    
    Returns:
        List of tools with name, description, and parameters information
    """
    # Get both regular and streaming tools
    regular_tools = get_tools()
    streaming_tools = get_streaming_tools()
    all_tools = regular_tools + streaming_tools
    
    tools_metadata = []
    
    for tool in all_tools:
        # Extract tool metadata
        tool_info = {
            "name": tool.name,
            "description": tool.description,
            "category": "Legal Analysis",
            "streaming": tool.name.startswith("streaming_"),
            "parameters": []
        }
        
        # Extract parameter information from the tool's args schema if available
        if hasattr(tool, 'args_schema') and tool.args_schema:
            schema = tool.args_schema.schema()
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for param_name, param_info in properties.items():
                param_data = {
                    "name": param_name,
                    "type": param_info.get('type', 'string'),
                    "description": param_info.get('description', ''),
                    "required": param_name in required,
                    "default": param_info.get('default')
                }
                tool_info["parameters"].append(param_data)
        
        tools_metadata.append(tool_info)
    
    # Sort tools: regular tools first, then streaming tools, alphabetically within each group
    tools_metadata.sort(key=lambda x: (x["streaming"], x["name"]))
    
    return tools_metadata


@router.get("/categories")
async def get_tool_categories():
    """
    Get available tool categories for filtering.
    
    Returns:
        List of tool categories
    """
    return [
        {
            "name": "Legal Analysis",
            "description": "Tools for analyzing legal cases, jurisdictions, and PIL principles",
            "count": len(get_tools()) + len(get_streaming_tools())
        }
    ]
