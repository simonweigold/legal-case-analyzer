import csv
import json
import re
from pathlib import Path
from typing import Union, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from config import llm

# Legal system type detection prompt
LEGAL_SYSTEM_TYPE_DETECTION_PROMPT = """
You are an expert legal scholar with deep knowledge of comparative legal systems worldwide. Your task is to analyze the provided text and classify it according to the legal system tradition it represents.

**CRITICAL INSTRUCTION: The jurisdiction name provided is HIGHLY RELIABLE and should take precedence over textual ambiguities.**

**CLASSIFICATION TASK:**
Determine if the text is from a:
1. "Civil-law jurisdiction" - Legal systems based on comprehensive written codes (Romano-Germanic tradition)
2. "Common-law jurisdiction" - Legal systems based on judicial precedents and case law (Anglo-American tradition) 
3. "No court decision" - Text that is not a judicial decision or cannot be classified

**ANALYSIS FRAMEWORK:**

**STEP 1: JURISDICTION-BASED CLASSIFICATION (PRIMARY)**
The provided jurisdiction is: {jurisdiction_name}

**Known Civil-Law Jurisdictions Include:**
- Switzerland, Germany, France, Italy, Spain, Austria, Netherlands, Belgium, Portugal, Greece
- Nordic countries: Finland, Sweden, Denmark, Norway, Iceland  
- Eastern Europe: Poland, Czech Republic, Slovakia, Hungary, Romania, Bulgaria, Croatia, Slovenia
- Baltic states: Estonia, Latvia, Lithuania
- Asia: Japan, South Korea, China, Taiwan, Thailand, Vietnam, Indonesia
- Latin America: Brazil, Argentina, Mexico, Chile, Colombia, Peru, Ecuador, Bolivia, Paraguay
- Middle East: Turkey, Egypt, Iran, Lebanon, Jordan, Kuwait, Qatar, UAE, Saudi Arabia
- Africa: Tunisia, Morocco, Algeria, Ethiopia, Angola, Mozambique
- Russia, Ukraine, and former Soviet states

**Known Common-Law Jurisdictions Include:**
- United States, United Kingdom (England, Scotland, Wales, Northern Ireland), Ireland
- Commonwealth: Canada, Australia, New Zealand, India, Pakistan, Bangladesh, Sri Lanka
- Southeast Asia: Malaysia, Singapore, Hong Kong, Philippines
- Africa: South Africa, Nigeria, Ghana, Kenya, Uganda, Tanzania, Zambia, Zimbabwe
- Caribbean: Jamaica, Barbados, Trinidad and Tobago, Bahamas, Belize

**STEP 2: TEXTUAL ANALYSIS (SECONDARY)**
Only if jurisdiction is unknown or ambiguous, examine text for:

**Civil-law indicators:**
- References to codes, statutes (e.g., "Article 123", "§ 242 BGB", "Code Civil")
- Systematic application of written law without extensive case citations
- Formal, deductive reasoning from general principles
- Court names: Bundesgerichtshof, Tribunal Federal, Cour de Cassation, Tribunal Supremo
- Swiss-specific: References to "Swiss Federal Act on Private International Law (PILA)", "Bundesgericht", "Tribunal fédéral"

**Common-law indicators:**
- Extensive case law citations with case names and years
- Reasoning through precedent and analogy ("distinguishing", "following")
- Terms: "plaintiff," "defendant," "holding," "ratio decidendi"
- Case styling: "[Name] v. [Name]"
- Court names: Supreme Court, Court of Appeals, High Court

**IMPORTANT NOTES:**
- Swiss court decisions are often published in English but Switzerland is definitively a CIVIL LAW jurisdiction
- Many civil law countries publish decisions in English for international accessibility
- Language alone should never override jurisdiction-based classification
- When jurisdiction clearly indicates one system but text suggests another, trust the jurisdiction

**OUTPUT REQUIREMENTS:**
Respond with exactly one of these phrases:
- Civil-law jurisdiction
- Common-law jurisdiction  
- No court decision

**TEXT TO ANALYZE:**
{text}
"""

# Precise jurisdiction detection prompt
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

**OUTPUT FORMAT:**
Respond with exactly: /"[Jurisdiction Name]"/

Where [Jurisdiction Name] is exactly as listed above, or "Unknown" if no match.

**TEXT TO ANALYZE:**
{text}
"""

def get_jurisdiction_legal_system_mapping():
    """
    Load jurisdiction to legal system mapping from jurisdictions.csv.
    Returns a dictionary mapping jurisdiction names to legal system types.
    """
    mapping = {}
    
    # Known civil law jurisdictions
    civil_law_jurisdictions = {
        'Switzerland', 'Germany', 'France', 'Italy', 'Spain', 'Austria', 'Netherlands', 'Belgium',
        'Luxembourg', 'Portugal', 'Greece', 'Finland', 'Sweden', 'Denmark', 'Norway', 'Poland',
        'Czech Republic', 'Slovakia', 'Hungary', 'Romania', 'Bulgaria', 'Croatia', 'Slovenia',
        'Estonia', 'Latvia', 'Lithuania', 'Malta', 'Cyprus', 'Japan', 'South Korea', 'China (Mainland)',
        'Taiwan', 'Brazil', 'Argentina', 'Mexico', 'Chile', 'Colombia', 'Peru', 'Ecuador',
        'Bolivia', 'Paraguay', 'Uruguay', 'Venezuela', 'Russia', 'Ukraine', 'Turkey', 'Egypt',
        'Morocco', 'Tunisia', 'Algeria', 'Iran', 'Lebanon', 'Jordan', 'Qatar', 'Kuwait', 'Bahrain',
        'UAE', 'Saudi Arabia', 'Israel', 'Indonesia', 'Thailand', 'Vietnam', 'Cambodia', 'Laos',
        'Ethiopia', 'Angola', 'Mozambique', 'Kazakhstan', 'Uzbekistan', 'Tajikistan', 'Kyrgyzstan',
        'Belarus', 'Moldova', 'Georgia', 'Armenia', 'Azerbaijan', 'Albania', 'Bosnia and Herzegovina',
        'North Macedonia', 'Montenegro', 'Serbia', 'Kosovo', 'Iceland', 'Liechtenstein', 'Monaco',
        'San Marino', 'Andorra', 'European Union', 'OHADA'
    }
    
    # Known common law jurisdictions
    common_law_jurisdictions = {
        'United States', 'United States of America', 'USA', 'United Kingdom', 'England', 'Scotland',
        'Wales', 'Northern Ireland', 'Ireland', 'Canada', 'Australia', 'New Zealand', 'India',
        'Pakistan', 'Bangladesh', 'Sri Lanka', 'Malaysia', 'Singapore', 'Hong Kong', 'South Africa',
        'Nigeria', 'Ghana', 'Kenya', 'Uganda', 'Tanzania', 'Zambia', 'Zimbabwe', 'Botswana',
        'Malawi', 'Sierra Leone', 'Gambia', 'Jamaica', 'Barbados', 'Trinidad and Tobago',
        'Bahamas', 'Belize', 'Guyana', 'Cyprus (Common Law aspects)', 'Malta (Common Law aspects)',
        'Israel (Common Law aspects)', 'Philippines', 'Myanmar'
    }
    
    # Create the mapping
    for jurisdiction in civil_law_jurisdictions:
        mapping[jurisdiction.lower()] = 'Civil-law jurisdiction'
    
    for jurisdiction in common_law_jurisdictions:
        mapping[jurisdiction.lower()] = 'Common-law jurisdiction'
    
    return mapping

def load_jurisdictions():
    """Load all jurisdictions from the CSV file."""
    jurisdictions_file = Path(__file__).parent.parent / 'data' / 'jurisdictions.csv'
    jurisdictions = []
    
    try:
        with open(jurisdictions_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Name'].strip():  # Only include rows with actual jurisdiction names
                    jurisdictions.append({
                        'name': row['Name'].strip(),
                        'code': row['Alpha-3 Code'].strip(),
                        'summary': row['Jurisdiction Summary'].strip()
                    })
    except FileNotFoundError:
        print(f"Warning: jurisdictions.csv not found at {jurisdictions_file}")
        return []
    
    # Sort jurisdictions by name for better consistency
    jurisdictions.sort(key=lambda x: x['name'].lower())
    return jurisdictions

def load_themes():
    """Load all legal themes from the CSV file."""
    themes_file = Path(__file__).parent.parent / 'data' / 'themes.csv'
    themes = []
    
    try:
        with open(themes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Theme'].strip():
                    themes.append({
                        'theme': row['Theme'].strip(),
                        'definition': row['Definition'].strip()
                    })
    except FileNotFoundError:
        print(f"Warning: themes.csv not found at {themes_file}")
        return []
    
    return themes

@tool
def detect_legal_system_type(jurisdiction_name: str = "", text: str = ""):
    """
    Detect the legal system type (Civil-law, Common-law, or No court decision) based on jurisdiction name and text analysis.
    
    Args:
        jurisdiction_name (str): The name of the jurisdiction where the case originates
        text (str): The legal case text to analyze
    
    Returns:
        str: 'Civil-law jurisdiction', 'Common-law jurisdiction', or 'No court decision'
    """
    if not text or len(text.strip()) < 50:
        return "No court decision"
    
    # First, try to determine based on jurisdiction name
    if jurisdiction_name and jurisdiction_name.lower() not in ['unknown', 'n/a', 'none']:
        mapping = get_jurisdiction_legal_system_mapping()
        
        # Direct lookup
        if jurisdiction_name.lower() in mapping:
            return mapping[jurisdiction_name.lower()]
        
        # Partial match lookup for compound names
        for mapped_jurisdiction, legal_system in mapping.items():
            if mapped_jurisdiction in jurisdiction_name.lower() or jurisdiction_name.lower() in mapped_jurisdiction:
                return legal_system
    
    # Fall back to LLM analysis
    prompt = LEGAL_SYSTEM_TYPE_DETECTION_PROMPT.format(jurisdiction_name=jurisdiction_name, text=text)
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are an expert in legal systems and court decisions."),
            HumanMessage(content=prompt)
        ])
        result = response.content.strip()
        
        # Enforce output to be one of the three categories
        allowed = ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"]
        for option in allowed:
            if option.lower() in result.lower():
                return option
        return "No court decision"
    except Exception as e:
        print(f"Error in legal system type detection: {e}")
        return "No court decision"

@tool
def detect_precise_jurisdiction(text: str = ""):
    """
    Identify the precise jurisdiction from court decision text using the jurisdictions database.
    
    Args:
        text (str): The court decision text to analyze
    
    Returns:
        str: The precise jurisdiction name or 'Unknown' if not identifiable
    """
    if not text or len(text.strip()) < 50:
        return "Unknown"
    
    jurisdictions = load_jurisdictions()
    if not jurisdictions:
        return "Unknown"
    
    # Create jurisdiction list for prompt
    jurisdiction_list = "\n".join([f"- {j['name']}" for j in jurisdictions])
    
    prompt = PRECISE_JURISDICTION_DETECTION_PROMPT.format(
        jurisdiction_list=jurisdiction_list,
        text=text[:5000]  # Limit text length to avoid token limits
    )
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are an expert in legal systems and court jurisdictions worldwide. Follow the format exactly as requested."),
            HumanMessage(content=prompt)
        ])
        
        result_text = response.content.strip()
        
        # Extract jurisdiction from the /"Jurisdiction"/ format
        jurisdiction_match = re.search(r'/\"([^\"]+)\"/', result_text)
        if jurisdiction_match:
            jurisdiction_name = jurisdiction_match.group(1)
        else:
            # Fallback: try to extract any quoted jurisdiction name
            quote_match = re.search(r'\"([^\"]+)\"', result_text)
            if quote_match:
                jurisdiction_name = quote_match.group(1)
            else:
                # Final fallback: use the entire response if it's reasonable
                if len(result_text) < 100 and result_text not in ['Unknown', 'unknown']:
                    jurisdiction_name = result_text.strip()
                else:
                    jurisdiction_name = "Unknown"
        
        # Validate jurisdiction against our list
        if jurisdiction_name and jurisdiction_name != "Unknown":
            # First try exact match
            for jurisdiction in jurisdictions:
                if jurisdiction['name'].lower() == jurisdiction_name.lower():
                    return jurisdiction['name']
            
            # Then try partial match (contains)
            for jurisdiction in jurisdictions:
                if jurisdiction_name.lower() in jurisdiction['name'].lower() or jurisdiction['name'].lower() in jurisdiction_name.lower():
                    return jurisdiction['name']
            
            # If no match found but we have a reasonable response, return it
            if len(jurisdiction_name) > 2 and jurisdiction_name not in ['Unknown', 'unknown', 'N/A', 'None']:
                return jurisdiction_name
        
        return "Unknown"
                
    except Exception as e:
        print(f"Error in precise jurisdiction detection: {e}")
        return "Unknown"

@tool
def extract_choice_of_law_section(text: str = ""):
    """
    Extract all portions of the judgment that discuss choice of law in private international law (PIL) contexts.
    
    Args:
        text (str): The full court decision text to analyze
    
    Returns:
        str: The extracted choice of law sections with court's reasoning
    """
    if not text or len(text.strip()) < 50:
        return "Insufficient text provided for choice of law analysis."
    
    col_prompt = """
TASK: Extract all portions of the judgment that discuss choice of law in private international law (PIL) contexts.

INSTRUCTIONS:
1. Scope of Extraction: Identify and extract the most important paragraphs, sentences, or sections where the court:
   - Determines the choice of law of the parties as per any rules of private international law
   - Discusses "applicable law," "proper law," "governing law," or "choice of law"
   - Analyzes party autonomy in law selection
   - Applies conflict of laws principles
   - References foreign legal systems in determining applicable law
   - Discusses the "closest connection" test or similar PIL methodologies

More specifically, when preparing the output, prioritize: 
(1) The court's direct conclusions about applicable law
(2) The court's reasoning about choice of law rules
(3) The court's analysis of contractual choice of law clauses
(4) The court's application of PIL principles

1.1 Make sure to include the following parts:
- The court's reasoning about law selection and analysis of party agreements on governing law
- Discussion of PIL principles and application of foreign law provisions
- Jurisdiction discussions ONLY when they directly involve choice of law analysis
- Supporting citations and precedents only when the court explicitly relies on them for its choice of law determination

1.2 Exclude all of the following:
- Pure procedural matters unrelated to choice of law
- Pure jurisdictional analysis that doesn't engage with PIL choice of law principles
- Enforcement issues not touching on choice of law
- Other matters on the merit of the dispute unrelated to choice of law or PIL
- Lengthy quotes from cited cases unless the court explicitly adopts them as part of its analysis

2. Extraction Method:
- Reproduce the court's exact language using quotation marks, abbreviating text using brackets [...] when necessary
- Extract complete sentences with essential context only
- Focus primarily on the court's own reasoning and analysis

3. Output Format:
[Section 1:] 
"[Exact court language]" 
[Section 2:] 
"[Exact court language]"

4. Quality Check:
- Ensure each extracted section shows the court's reasoning chain
- Break longer passages into separate sections if they address different choice of law issues
- If necessary, add brackets […] to abbreviate the text if it touches upon matters included in the exclusion list

5. CONSTRAINT: Base extraction solely on the provided judgment text. Do not add interpretive commentary or external legal knowledge.

Here is the text of the Court Decision:
{text}

Here is the section of the Court Decision containing Choice of Law related information:
"""
    
    try:
        prompt = col_prompt.format(text=text)
        response = llm.invoke([
            SystemMessage(content="You are an expert in private international law and choice of law analysis."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        return f"Error in choice of law extraction: {e}"

@tool
def classify_legal_themes(text: str = "", col_section: str = ""):
    """
    Classify legal themes based on provided themes database and case analysis.
    
    Args:
        text (str): The full court decision text
        col_section (str): The extracted choice of law section
    
    Returns:
        str: Comma-separated list of identified legal themes
    """
    if not text or len(text.strip()) < 50:
        return "Insufficient text provided for theme classification."
    
    themes = load_themes()
    if not themes:
        return "Theme database not available."
    
    # Create themes table string
    themes_table = "\n".join([f"- {theme['theme']}: {theme['definition']}" for theme in themes])
    valid_theme_names = [theme['theme'] for theme in themes]
    
    theme_prompt = """
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
    
    try:
        prompt = theme_prompt.format(
            text=text[:3000],  # Limit text length
            col_section=col_section,
            themes_table=themes_table
        )
        
        # Attempt classification up to 3 times to ensure valid themes
        for attempt in range(3):
            response = llm.invoke([
                SystemMessage(content="You are an expert in private international law. Return only valid themes as JSON."),
                HumanMessage(content=prompt)
            ])
            
            try:
                # Try to parse as JSON
                result_list = json.loads(response.content)
                # Validate themes
                invalid = [item for item in result_list if item not in valid_theme_names]
                if not invalid:
                    return ", ".join(result_list)
            except json.JSONDecodeError:
                # Try to extract themes from text response
                result_list = [theme.strip() for theme in response.content.split(',')]
            
            # If still invalid themes, continue loop
            invalid = [item for item in result_list if item not in valid_theme_names]
            if not invalid:
                return ", ".join(result_list)
        
        # Fallback: return the last attempt
        return ", ".join([str(item) for item in result_list if str(item) in valid_theme_names])
        
    except Exception as e:
        return f"Error in theme classification: {e}"

@tool
def identify_choice_of_law_issue(text: str = "", col_section: str = "", themes: str = ""):
    """
    Identify and analyze the specific choice of law issue presented in the case.
    
    Args:
        text (str): The full court decision text
        col_section (str): The extracted choice of law section
        themes (str): Comma-separated list of classified themes
    
    Returns:
        str: Analysis of the choice of law issue in the case
    """
    if not text or len(text.strip()) < 50:
        return "Insufficient text provided for choice of law issue analysis."
    
    # Load theme definitions for context
    theme_definitions = ""
    if themes:
        themes_list = [t.strip() for t in themes.split(',')]
        all_themes = load_themes()
        relevant_themes = [t for t in all_themes if t['theme'] in themes_list]
        theme_definitions = "\n".join([f"- {theme['theme']}: {theme['definition']}" for theme in relevant_themes])
    
    issue_prompt = """
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
    
    try:
        prompt = issue_prompt.format(
            text=text[:3000],  # Limit text length
            col_section=col_section,
            theme_definitions=theme_definitions
        )
        
        response = llm.invoke([
            SystemMessage(content="You are an expert in private international law and choice of law analysis."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        return f"Error in choice of law issue identification: {e}"

@tool
def analyze_courts_position(text: str = "", col_section: str = "", themes: str = "", col_issue: str = ""):
    """
    Analyze the court's position and reasoning on the choice of law matter.
    
    Args:
        text (str): The full court decision text
        col_section (str): The extracted choice of law section
        themes (str): Comma-separated list of classified themes
        col_issue (str): The identified choice of law issue
    
    Returns:
        str: Analysis of the court's position and reasoning
    """
    if not text or len(text.strip()) < 50:
        return "Insufficient text provided for court position analysis."
    
    position_prompt = """
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
    
    try:
        prompt = position_prompt.format(
            text=text[:3000],  # Limit text length
            col_section=col_section,
            themes=themes,
            col_issue=col_issue
        )
        
        response = llm.invoke([
            SystemMessage(content="You are an expert in private international law and judicial analysis."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        return f"Error in court position analysis: {e}"

@tool
def analyze_legal_case(case_details: str = ""):
    """
    Analyze legal case details and provide comprehensive PIL insights using advanced analysis tools.
    
    Args:
        case_details (str): The details of the legal case to analyze. 
                           Include facts, issues, relevant laws, parties involved, etc.
                           If no details provided, will ask for more information.
    
    Returns:
        str: Comprehensive legal analysis with PIL focus and recommendations.
    """
    if not case_details or case_details.strip() == "":
        return ("Please provide the legal case details you would like me to analyze. "
                "Include relevant facts, legal issues, parties involved, jurisdiction, "
                "and any specific areas of concern.")
    
    try:
        # Step 1: Detect jurisdiction and legal system
        jurisdiction = detect_precise_jurisdiction(case_details)
        legal_system = detect_legal_system_type(jurisdiction, case_details)
        
        # Step 2: Extract choice of law sections
        col_section = extract_choice_of_law_section(case_details)
        
        # Step 3: Classify themes
        themes = classify_legal_themes(case_details, col_section)
        
        # Step 4: Identify choice of law issue
        col_issue = identify_choice_of_law_issue(case_details, col_section, themes)
        
        # Step 5: Analyze court's position
        courts_position = analyze_courts_position(case_details, col_section, themes, col_issue)
        
        # Compile comprehensive analysis
        analysis = f"""COMPREHENSIVE LEGAL CASE ANALYSIS

**JURISDICTION & LEGAL SYSTEM:**
- Jurisdiction: {jurisdiction}
- Legal System Type: {legal_system}

**CHOICE OF LAW ANALYSIS:**
{col_section}

**IDENTIFIED THEMES:**
{themes}

**CHOICE OF LAW ISSUE:**
{col_issue}

**COURT'S POSITION:**
{courts_position}

**RECOMMENDATIONS:**
- Consider the court's reasoning for future similar cases
- Review the applicable PIL principles identified
- Analyze the practical implications of the chosen law
- Consult qualified legal professionals for case-specific advice

Note: This analysis is for educational and research purposes. Please consult with qualified legal professionals for actual legal matters."""

        return analysis
        
    except Exception as e:
        return f"Error in comprehensive legal case analysis: {e}"

@tool
def welcome_user():
    """
    Welcome the user to the Legal Case Analyzer toolset.
    
    Returns:
        str: A welcome message.
    """
    return ("Welcome to the Legal Case Analyzer! You can use the available tools "
            "to analyze legal cases and search for relevant legal precedents. "
            "Please provide the necessary details to get started.")

@tool
def welcome_user():
    """
    Welcome the user to the Legal Case Analyzer toolset.
    
    Returns:
        str: A welcome message.
    """
    return ("Welcome to the Legal Case Analyzer! You can use the available tools "
            "to analyze legal cases and search for relevant legal precedents. "
            "Please provide the necessary details to get started.")

@tool
def analyze_legal_case(case_details: str = ""):
    """
    Analyze legal case details and provide insights.
    
    Args:
        case_details (str): The details of the legal case to analyze. 
                           Include facts, issues, relevant laws, parties involved, etc.
                           If no details provided, will ask for more information.
    
    Returns:
        str: Legal analysis with key considerations and recommendations.
    """
    if not case_details or case_details.strip() == "":
        return ("Please provide the legal case details you would like me to analyze. "
                "Include relevant facts, legal issues, parties involved, jurisdiction, "
                "and any specific areas of concern.")
    
    # This is a placeholder for actual legal case analysis
    # In a real implementation, this would connect to legal databases or analysis tools
    return f"""Legal case analysis for: {case_details}

Key considerations:
- Precedent review needed
- Statutory compliance check required  
- Risk assessment: Medium
- Recommended next steps: Research similar cases, consult relevant statutes

Please note: This analysis should not replace consultation with qualified legal professionals."""


@tool
def search_legal_precedents(query: str = ""):
    """
    Search for legal precedents related to a query.
    
    Args:
        query (str): The search query for finding relevant legal precedents.
                    Include key legal concepts, issues, or case types.
    
    Returns:
        str: List of relevant legal precedents and cases.
    """
    if not query or query.strip() == "":
        return "Please provide a search query to find relevant legal precedents."
    
    # Placeholder for legal precedent search
    return f"""Found relevant precedents for '{query}':

1. Case A vs B (2020) - Similar circumstances, established principle of X
2. Case C vs D (2019) - Related legal principle, addressed issue Y  
3. Case E vs F (2018) - Applicable statute interpretation for Z

Note: These are example results. In practice, this would search actual legal databases."""


def get_tools():
    """Get all available tools."""
    return [
        welcome_user,
        detect_legal_system_type,
        detect_precise_jurisdiction,
        extract_choice_of_law_section,
        classify_legal_themes,
        identify_choice_of_law_issue,
        analyze_courts_position,
        analyze_legal_case,
        search_legal_precedents
    ]


def get_tools_by_name():
    """Get tools indexed by name."""
    tools = get_tools()
    return {tool.name: tool for tool in tools}
