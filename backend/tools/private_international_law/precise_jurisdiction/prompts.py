from .jurisdictions import JURISDICTION_NAMES

# Build the static jurisdiction list once. This avoids dynamic CSV loading and
# keeps the tool autonomous.
_JURISDICTION_BULLET_LIST = "\n".join(f"- {name}" for name in JURISDICTION_NAMES)

PRECISE_JURISDICTION_DETECTION_PROMPT = """
You are an expert in legal systems and court jurisdictions worldwide. Your task is to identify the precise jurisdiction from the provided court decision text.

**AVAILABLE JURISDICTIONS:**
{jurisdiction_list}

**INSTRUCTIONS:**
1. Analyze the court decision text carefully
2. Look for explicit mentions of:
   - Court names and their locations
   - Legal system references
   - Geographic indicators
   - Language patterns
   - Legal concepts specific to certain jurisdictions

3. Match the identified jurisdiction with one from the available list above
4. If uncertain or no clear match, respond with "Unknown"

**STRICT OUTPUT FORMAT (machine parseable):**
Return exactly one line:
"/[Jurisdiction Name]/"

Where [Jurisdiction Name] is one of the entries above, or "Unknown" if no match.

Do not add explanations or additional text outside the delimiter format in your direct answer.

**TEXT TO ANALYZE (truncated if long):**
{text}
""".strip()

def build_precise_jurisdiction_prompt(text: str) -> str:
	"""Return the filled prompt with embedded jurisdiction list and truncated text."""
	print("the prompt is: ", PRECISE_JURISDICTION_DETECTION_PROMPT.format(
		jurisdiction_list=_JURISDICTION_BULLET_LIST,
		text=text[:50000]
	))
	return PRECISE_JURISDICTION_DETECTION_PROMPT.format(
		jurisdiction_list=_JURISDICTION_BULLET_LIST,
		text=text[:50000]
	)

