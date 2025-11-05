try:
    from langchain_core.tools import tool
except ImportError:  # pragma: no cover
    def tool(fn):
        return fn


from .prompts import WELCOME_PROMPT

@tool
def welcome_user():
    """Welcome message summarizing available tool capabilities."""
    return WELCOME_PROMPT
