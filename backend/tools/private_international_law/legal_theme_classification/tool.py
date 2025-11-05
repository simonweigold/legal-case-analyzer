import json
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
from .prompts import LEGAL_THEME_CLASSIFICATION_PROMPT


@tool
def classify_legal_themes(text: str = "", col_section: str = ""):
    """Classify legal themes based on the themes database and case analysis."""
    if not text or len(text.strip()) < 50:
        return ("**Theme Classification: Insufficient Text**\n\n" \
                "The provided text is too short to analyze for legal themes. Please provide a complete court decision that contains PIL analysis or choice of law discussions.")
    try:
        themes = load_themes()
        if not themes:
            return ("**Theme Classification: Database Error**\n\n" \
                    "Unable to load the themes database. The system cannot perform theme classification without access to the reference themes. Please check that the themes.csv file is properly installed.")
        themes_table = "\n".join([f"- {theme['theme']}: {theme['definition']}" for theme in themes])
        valid_theme_names = [theme['theme'] for theme in themes]
        prompt = LEGAL_THEME_CLASSIFICATION_PROMPT.format(
            text=text[:3000],
            col_section=col_section[:2000] if col_section else "No specific choice of law section provided",
            themes_table=themes_table
        )
        classified_themes = []
        for attempt in range(3):
            response = llm.invoke([
                SystemMessage(content="You are an expert in private international law. Return only valid themes as JSON."),
                HumanMessage(content=prompt)
            ])
            try:
                result_list = json.loads(response.content)
                invalid = [item for item in result_list if item not in valid_theme_names]
                if not invalid:
                    classified_themes = result_list
                    break
            except json.JSONDecodeError:
                result_list = [theme.strip() for theme in response.content.split(',')]
                valid_results = [item for item in result_list if item in valid_theme_names]
                if valid_results:
                    classified_themes = valid_results
                    break
        if classified_themes:
            theme_explanations = []
            for theme_name in classified_themes:
                for theme in themes:
                    if theme['theme'] == theme_name:
                        theme_explanations.append(
                            f"**{theme_name}**: {theme['definition'][:200]}" + ('...' if len(theme['definition']) > 200 else '')
                        )
                        break
            result = "**Theme Classification Analysis**\n\nThe following legal themes have been identified in this case:\n\n"
            result += f"**Identified Themes:** {', '.join(classified_themes)}\n\n"
            result += "**Theme Definitions:**\n" + "\n\n".join(theme_explanations)
            return result
        else:
            return ("**Theme Classification: No Specific PIL Themes Identified**\n\n" \
                    "After analysis, no specific private international law themes from the reference database were clearly identified in this case. This may indicate that the case involves general PIL principles without focusing on specific themes like party autonomy, mandatory rules, or consumer contracts, or the case may primarily involve domestic legal issues.")
    except Exception as e:
        return ("**Theme Classification: Analysis Error**\n\n" \
                f"Unable to complete theme classification due to technical error: {str(e)}. This may be due to LLM service issues, database access problems, or text processing errors. Please try again or provide alternative text.")
