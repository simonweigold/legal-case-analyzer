COURT_POSITION_PROMPT = """
You are an expert in private international law (PIL). Analyze the court's position and reasoning regarding the choice of law matter in this case.

INSTRUCTIONS:
1. Identify the court's final conclusion on the choice of law question
2. Analyze the court's reasoning process and legal methodology
3. Identify the legal principles, rules, or precedents the court relied upon
4. Evaluate the court's application of PIL concepts
5. Note any innovative approaches or significant interpretations
6. Discuss the practical implications of the court's decision

CHOICE OF LAW ISSUE:
{col_issue}

COURT DECISION TEXT:
{text}

CHOICE OF LAW SECTION:
{col_section}

CLASSIFIED THEMES: {themes}

Provide a comprehensive analysis of the court's position:
"""
