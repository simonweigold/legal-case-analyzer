CHOICE_OF_LAW_ISSUE_PROMPT = """
You are an expert in private international law (PIL). Analyze the court decision and identify the specific choice of law issue(s) presented in the case.

RELEVANT THEME DEFINITIONS:
{theme_definitions}

INSTRUCTIONS:
1. Identify the core choice of law problem the court had to resolve
2. Explain what legal question required choice of law analysis
3. Describe any conflicting laws or jurisdictions involved
4. Highlight the key legal principles or rules applied
5. Focus on the PIL-specific aspects of the case

COURT DECISION TEXT:
{text}

CHOICE OF LAW SECTION:
{col_section}

Provide a clear analysis of the choice of law issue:
"""
