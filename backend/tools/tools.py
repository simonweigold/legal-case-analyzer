"""Backward-compatible tool re-exports after modular refactor.

This file now simply re-exports the individual tool functions that have been
split into dedicated subpackages with separated prompts and core logic.
Existing imports of `backend.tools.tools` should continue to work.
"""

#from .welcome import welcome_user
from .private_international_law.precise_jurisdiction.tool import detect_precise_jurisdiction
from .private_international_law.legal_system_type.tool import detect_legal_system_type
from .private_international_law.choice_of_law_extraction.tool import extract_choice_of_law_section

def get_tools():  # pragma: no cover - simple list construction
    return [
            #welcome_user,
            detect_precise_jurisdiction,
            detect_legal_system_type,
            extract_choice_of_law_section
            ]


def get_tools_by_name():  # pragma: no cover
    return {tool.name: tool for tool in get_tools()}
