LEGAL_THEME_CLASSIFICATION_PROMPT = """
You are an expert in private international law (PIL) and choice of law analysis. Your task is to classify the legal themes present in the provided court decision.

AVAILABLE THEMES:
{themes_table}

INSTRUCTIONS:
1. Analyze the court decision text and the extracted choice of law section
2. Identify which of the available themes are present in the case
3. Focus on themes that are actually discussed or applied by the court
4. Return ONLY themes from the available list above
5. Return themes as a JSON list of strings, e.g., ["Party autonomy", "Absence of choice"]

COURT DECISION TEXT:
{text}

CHOICE OF LAW SECTION:
{col_section}

Return only the JSON list of applicable themes:
"""
