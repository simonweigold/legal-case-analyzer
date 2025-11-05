try:
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:  # pragma: no cover
    def tool(fn):
        return fn
    class _Msg:
        def __init__(self, content: str):
            self.content = content
    HumanMessage = SystemMessage = _Msg
from config import llm
from .prompts import COURT_POSITION_PROMPT


@tool
def analyze_courts_position(text: str = "", col_section: str = "", themes: str = "", col_issue: str = ""):
    """Analyze court's position and reasoning on the choice of law matter."""
    if not text or len(text.strip()) < 50:
        return ("**Court Position Analysis: Insufficient Text**\n\n" \
                "The provided text is too short to analyze the court's position on choice of law matters. Please provide a complete court decision that contains PIL analysis and reasoning.")
    try:
        prompt = COURT_POSITION_PROMPT.format(
            col_issue=col_issue[:1000] if col_issue else "No specific choice of law issue identified",
            text=text[:3000],
            col_section=col_section[:2000] if col_section else "No specific choice of law section provided",
            themes=themes if themes else "No specific themes identified"
        )
        response = llm.invoke([
            SystemMessage(content="You are an expert in private international law and judicial analysis. Provide thorough analysis of court reasoning."),
            HumanMessage(content=prompt)
        ])
        court_analysis = response.content.strip()
        if court_analysis and len(court_analysis) > 50:
            return ("**Court Position Analysis**\n\n" \
                    f"{court_analysis}\n\n**Note:** This analysis examines the court's reasoning process, legal methodology, and the practical implications of its choice of law determination.")
        else:
            return ("**Court Position Analysis: No Clear Court Position Identified**\n\n" \
                    "After analysis, no clear court position on choice of law matters could be identified in this case. This may indicate that the case does not contain explicit PIL reasoning, or the court's position may not be clearly articulated in the available text.")
    except Exception as e:
        return ("**Court Position Analysis: Analysis Error**\n\n" \
                f"Unable to complete court position analysis due to technical error: {str(e)}. This may be due to LLM service issues, input processing problems, or network connectivity issues. Please try again.")
