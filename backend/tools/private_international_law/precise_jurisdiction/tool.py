import re
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
from .jurisdictions import JURISDICTION_NAMES
from .prompts import build_precise_jurisdiction_prompt


@tool
def detect_precise_jurisdiction(text: str = ""):
    """Identify precise jurisdiction from court decision text using embedded jurisdiction list.

    Returns a markdown explanation with detection result and (if found) a short rationale.
    """
    if not text or len(text.strip()) < 50:
        return (
            "**Jurisdiction Detection: Insufficient Text**\n\n"
            "Provide a longer decision excerpt (≥50 chars) including court names, locations, or legal references."
        )
    try:
        prompt = build_precise_jurisdiction_prompt(text)
        response = llm.invoke([
            SystemMessage(content="You are an expert in legal systems and court jurisdictions worldwide. Output strictly as instructed."),
            HumanMessage(content=prompt)
        ])
        raw = response.content.strip()
        match = re.search(r'/"([^"]+)"/', raw)
        jurisdiction_name = match.group(1) if match else "Unknown"

        if jurisdiction_name != "Unknown":
            # Exact match check against embedded list.
            normalized = jurisdiction_name.lower()
            names_lower = [n.lower() for n in JURISDICTION_NAMES]
            if normalized in names_lower:
                canonical = JURISDICTION_NAMES[names_lower.index(normalized)]
                return (
                    f"**Jurisdiction Detection: {canonical}**\n\n"
                    f"Identified **{canonical}** based on textual indicators (court/org names, geographic/legal references)."
                )
            # Fallback partial suggestion
            partial = next((n for n in JURISDICTION_NAMES if normalized in n.lower() or n.lower() in normalized), None)
            if partial:
                return (
                    f"**Jurisdiction Detection: {partial} (Partial Match)**\n\n"
                    f"Model returned '{jurisdiction_name}'. Closest known jurisdiction: **{partial}**."
                )
            return (
                f"**Jurisdiction Detection: {jurisdiction_name} (Unverified)**\n\n"
                "Returned value not found in embedded list; may be a sub-national entity or unsupported jurisdiction."
            )
        return (
            "**Jurisdiction Detection: Unknown**\n\n"
            "No definitive jurisdiction could be extracted from the supplied text. Provide more explicit court or location references."
        )
    except Exception as e:  # pragma: no cover
        return (
            "**Jurisdiction Detection: Analysis Error**\n\n"
            f"Internal error: {e}. Retry with different text or after system check."
        )
