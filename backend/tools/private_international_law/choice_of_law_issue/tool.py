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
from ..shared import load_themes
from .prompts import CHOICE_OF_LAW_ISSUE_PROMPT


@tool
def identify_choice_of_law_issue(text: str = "", col_section: str = "", themes: str = ""):
    """Identify and analyze specific choice of law issue(s) in the case."""
    if not text or len(text.strip()) < 50:
        return ("**Choice of Law Issue Analysis: Insufficient Text**\n\n" \
                "The provided text is too short to analyze for choice of law issues. Please provide a complete court decision that contains PIL analysis or choice of law discussions.")
    try:
        theme_definitions = ""
        if themes:
            themes_list = [t.strip() for t in themes.split(',')]
            all_themes = load_themes()
            if all_themes:
                relevant = [t for t in all_themes if t['theme'] in themes_list]
                theme_definitions = "\n".join([f"- {t['theme']}: {t['definition']}" for t in relevant])
        prompt = CHOICE_OF_LAW_ISSUE_PROMPT.format(
            theme_definitions=theme_definitions if theme_definitions else "No specific themes identified",
            text=text[:3000],
            col_section=col_section[:2000] if col_section else "No specific choice of law section provided"
        )
        response = llm.invoke([
            SystemMessage(content="You are an expert in private international law and choice of law analysis. Provide detailed analysis of PIL issues."),
            HumanMessage(content=prompt)
        ])
        issue_analysis = response.content.strip()
        if issue_analysis and len(issue_analysis) > 50:
            return ("**Choice of Law Issue Analysis**\n\n" \
                    f"{issue_analysis}\n\n**Note:** This analysis focuses on the specific PIL challenges and choice of law determinations that the court needed to address in reaching its decision.")
        else:
            return ("**Choice of Law Issue Analysis: No Clear PIL Issues Identified**\n\n" \
                    "After analysis, no specific choice of law issues were clearly identified in this case. This may indicate that the case primarily involves domestic law applications, or the PIL aspects may not be explicitly discussed in the available text.")
    except Exception as e:
        return ("**Choice of Law Issue Analysis: Analysis Error**\n\n" \
                f"Unable to complete choice of law issue analysis due to technical error: {str(e)}. This may be due to LLM service issues, theme database access problems, or text processing errors. Please try again.")
