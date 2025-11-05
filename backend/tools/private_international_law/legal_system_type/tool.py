try:  # Graceful fallback if langchain_core isn't available at static analysis time
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
from ..shared import get_jurisdiction_legal_system_mapping
from .prompts import LEGAL_SYSTEM_TYPE_DETECTION_PROMPT


@tool
def detect_legal_system_type(jurisdiction_name: str = "", text: str = ""):
    """Detect legal system type based on jurisdiction name and text (Civil-law / Common-law / No court decision)."""
    if not text or len(text.strip()) < 50:
        return ("**Legal System Analysis: No court decision**\n\n" \
                "The provided text is too short or empty to analyze as a court decision. "
                "Please provide a more substantial legal text for analysis.")
    try:
        if jurisdiction_name and jurisdiction_name.lower() not in ['unknown', 'n/a', 'none']:
            mapping = get_jurisdiction_legal_system_mapping()
            if jurisdiction_name.lower() in mapping:
                system_type = mapping[jurisdiction_name.lower()]
                return (f"**Legal System Analysis: {system_type}**\n\n" \
                        f"Based on jurisdiction mapping, '{jurisdiction_name}' is classified as a {system_type.lower()}. "
                        "This classification is based on the established legal tradition and institutional framework of the jurisdiction.")
            for mapped_jurisdiction, legal_system in mapping.items():
                if mapped_jurisdiction in jurisdiction_name.lower() or jurisdiction_name.lower() in mapped_jurisdiction:
                    return (f"**Legal System Analysis: {legal_system}**\n\n" \
                            f"Based on partial jurisdiction matching ('{jurisdiction_name}' matches '{mapped_jurisdiction}'), this appears to be a {legal_system.lower()}. "
                            "The classification is based on the established legal tradition of the broader jurisdiction.")
        prompt = LEGAL_SYSTEM_TYPE_DETECTION_PROMPT.format(jurisdiction_name=jurisdiction_name, text=text)
        response = llm.invoke([
            SystemMessage(content="You are an expert in legal systems and court decisions."),
            HumanMessage(content=prompt)
        ])
        result = response.content.strip()
        allowed = ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"]
        for option in allowed:
            if option.lower() in result.lower():
                return (f"**Legal System Analysis: {option}**\n\n" \
                        f"Based on textual analysis of the court decision, this has been classified as a {option.lower()}. "
                        "The analysis considered legal terminology, citation patterns, reasoning structure, and institutional references typical of this legal system tradition.")
        return ("**Legal System Analysis: No court decision**\n\n" \
                "After analyzing the provided text, it does not appear to be a formal court decision from either civil-law or common-law traditions. "
                "The text may be academic, legislative, or administrative in nature.")
    except Exception as e:
        return ("**Legal System Analysis: Analysis Error**\n\n" \
                f"Unable to complete legal system type detection due to technical error: {str(e)}. Please try again or provide alternative text for analysis. If the problem persists, the LLM service may be unavailable.")
