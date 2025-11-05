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
from .prompts import (
    CHOICE_OF_LAW_EXTRACTION_CIVIL_LAW_PROMPT,
    CHOICE_OF_LAW_EXTRACTION_COMMON_LAW_PROMPT,
)


@tool
def extract_choice_of_law_section(text: str = "", jurisdiction_type: str = ""):
    """Extract judgment portions discussing choice of law in PIL contexts.

    Parameters:
        text (str): Full court decision text to analyze.
        jurisdiction_type (str): Either 'civil law' or 'common law' specifying the legal tradition of the decision.

    Returns:
        str: Formatted extraction or informative message.
    """
    if not text or len(text.strip()) < 50:
        return (
            "**Choice of Law Extraction: Insufficient Text**\n\n"
            "The provided text is too short to contain meaningful choice of law analysis. Provide a complete court decision containing choice of/applicable law reasoning."
        )

    if not jurisdiction_type or jurisdiction_type.strip().lower() not in {"civil law", "common law"}:
        return (
            "**Choice of Law Extraction: Invalid Jurisdiction Type**\n\n"
            "Please supply jurisdiction_type='civil law' or 'common law' to tailor extraction to the appropriate legal tradition."
        )

    jt = jurisdiction_type.strip().lower()
    if jt == "civil law":
        base_prompt = CHOICE_OF_LAW_EXTRACTION_CIVIL_LAW_PROMPT
    else:
        base_prompt = CHOICE_OF_LAW_EXTRACTION_COMMON_LAW_PROMPT

    try:
        prompt = base_prompt.format(text=text[:8000])
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are an expert in private international law and choice of law analysis. "
                        "Extract relevant sections accurately and comprehensively, strictly following the given instructions."
                    )
                ),
                HumanMessage(content=prompt),
            ]
        )
        extracted_content = getattr(response, "content", "").strip()
        if extracted_content and len(extracted_content) > 50:
            header = "**Choice of Law Section Extraction**\n\n"
            intro = (
                "The following sections from the court decision discuss choice of law and private international law principles ("\
                f"jurisdiction type: {jt}).\n\n"
            )
            note = (
                "\n\n**Note:** Extraction tailored to the "
                f"{jt} tradition, focusing on applicable law reasoning, choice of law clauses, and PIL principles as expressed in the judgment's own language."
            )
            return f"{header}{intro}{extracted_content}{note}"
        else:
            return (
                "**Choice of Law Extraction: No PIL Discussion Found**\n\n"
                "No substantive discussion of choice/applicable law or private international law principles detected in the supplied text using the "
                f"{jt} prompt variant. The decision may be purely domestic or lacks explicit PIL analysis."
            )
    except Exception as e:
        return (
            "**Choice of Law Extraction: Analysis Error**\n\n"
            f"Failed during extraction for jurisdiction type '{jt}': {str(e)}"
        )
