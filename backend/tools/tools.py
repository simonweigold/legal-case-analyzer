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
        str: Analysis result with legal system type and reasoning
    """
    if not text or len(text.strip()) < 50:
        return "**Legal System Analysis: No court decision**\n\nThe provided text is too short or empty to analyze as a court decision. Please provide a more substantial legal text for analysis."
    
    try:
        # First, try to determine based on jurisdiction name
        if jurisdiction_name and jurisdiction_name.lower() not in ['unknown', 'n/a', 'none']:
            mapping = get_jurisdiction_legal_system_mapping()
            
            # Direct lookup
            if jurisdiction_name.lower() in mapping:
                system_type = mapping[jurisdiction_name.lower()]
                return f"**Legal System Analysis: {system_type}**\n\nBased on jurisdiction mapping, '{jurisdiction_name}' is classified as a {system_type.lower()}. This classification is based on the established legal tradition and institutional framework of the jurisdiction."
            
            # Partial match lookup for compound names
            for mapped_jurisdiction, legal_system in mapping.items():
                if mapped_jurisdiction in jurisdiction_name.lower() or jurisdiction_name.lower() in mapped_jurisdiction:
                    return f"**Legal System Analysis: {legal_system}**\n\nBased on partial jurisdiction matching ('{jurisdiction_name}' matches '{mapped_jurisdiction}'), this appears to be a {legal_system.lower()}. The classification is based on the established legal tradition of the broader jurisdiction."
        
        # Fall back to LLM analysis
        prompt = LEGAL_SYSTEM_TYPE_DETECTION_PROMPT.format(jurisdiction_name=jurisdiction_name, text=text)
        
        response = llm.invoke([
            SystemMessage(content="You are an expert in legal systems and court decisions."),
            HumanMessage(content=prompt)
        ])
        result = response.content.strip()
        
        # Enforce output to be one of the three categories
        allowed = ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"]
        for option in allowed:
            if option.lower() in result.lower():
                return f"**Legal System Analysis: {option}**\n\nBased on textual analysis of the court decision, this has been classified as a {option.lower()}. The analysis considered legal terminology, citation patterns, reasoning structure, and institutional references typical of this legal system tradition."
        
        return "**Legal System Analysis: No court decision**\n\nAfter analyzing the provided text, it does not appear to be a formal court decision from either civil-law or common-law traditions. The text may be academic, legislative, or administrative in nature."
        
    except Exception as e:
        return f"**Legal System Analysis: Analysis Error**\n\nUnable to complete legal system type detection due to technical error: {str(e)}. Please try again or provide alternative text for analysis. If the problem persists, the LLM service may be unavailable."

@tool
def detect_precise_jurisdiction(text: str = ""):
    """
    Identify the precise jurisdiction from court decision text using the jurisdictions database.
    
    Args:
        text (str): The court decision text to analyze
    
    Returns:
        str: Detailed analysis with the precise jurisdiction name and reasoning
    """
    if not text or len(text.strip()) < 50:
        return "**Jurisdiction Detection: Insufficient Text**\n\nThe provided text is too short to analyze for jurisdiction identification. Please provide a more substantial court decision text that includes court names, legal references, or geographic indicators."
    
    try:
        jurisdictions = load_jurisdictions()
        if not jurisdictions:
            return "**Jurisdiction Detection: Database Error**\n\nUnable to load the jurisdictions database. The system cannot perform jurisdiction detection without access to the reference data. Please check the data files are properly installed."
        
        # Create jurisdiction list for prompt
        jurisdiction_list = "\n".join([f"- {j['name']}" for j in jurisdictions])
        
        prompt = PRECISE_JURISDICTION_DETECTION_PROMPT.format(
            jurisdiction_list=jurisdiction_list,
            text=text[:5000]  # Limit text length to avoid token limits
        )
        
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
                    summary = jurisdiction.get('summary', 'No additional information available.')
                    return f"**Jurisdiction Detection: {jurisdiction['name']}**\n\nThe court decision has been identified as originating from **{jurisdiction['name']}** based on textual analysis of court references, legal terminology, and institutional indicators.\n\n**Jurisdiction Summary:**\n{summary[:500]}{'...' if len(summary) > 500 else ''}"
            
            # Then try partial match (contains)
            for jurisdiction in jurisdictions:
                if jurisdiction_name.lower() in jurisdiction['name'].lower() or jurisdiction['name'].lower() in jurisdiction_name.lower():
                    summary = jurisdiction.get('summary', 'No additional information available.')
                    return f"**Jurisdiction Detection: {jurisdiction['name']} (Partial Match)**\n\nThe court decision appears to originate from **{jurisdiction['name']}** based on partial matching with '{jurisdiction_name}'. This classification is based on textual analysis of legal references and terminology.\n\n**Jurisdiction Summary:**\n{summary[:500]}{'...' if len(summary) > 500 else ''}"
            
            # If no match found but we have a reasonable response, return it
            if len(jurisdiction_name) > 2 and jurisdiction_name not in ['Unknown', 'unknown', 'N/A', 'None']:
                return f"**Jurisdiction Detection: {jurisdiction_name} (Unverified)**\n\nThe analysis suggests the jurisdiction is **{jurisdiction_name}**, but this could not be verified against the standard jurisdictions database. This may be a regional court, specialized tribunal, or the jurisdiction name may not exactly match database entries."
        
        return f"**Jurisdiction Detection: Unknown**\n\nUnable to identify the precise jurisdiction from the provided court decision text. The text may lack sufficient geographic or institutional indicators, or may originate from a jurisdiction not included in the reference database. Consider providing additional context or a more complete court decision text."
                
    except Exception as e:
        return f"**Jurisdiction Detection: Analysis Error**\n\nUnable to complete jurisdiction detection due to technical error: {str(e)}. This may be due to LLM service unavailability, network issues, or text processing errors. Please try again or provide alternative text."

@tool
def extract_choice_of_law_section(text: str = ""):
    """
    Extract all portions of the judgment that discuss choice of law in private international law (PIL) contexts.
    
    Args:
        text (str): The full court decision text to analyze
    
    Returns:
        str: The extracted choice of law sections with court's reasoning and detailed analysis
    """
    if not text or len(text.strip()) < 50:
        return "**Choice of Law Extraction: Insufficient Text**\n\nThe provided text is too short to contain meaningful choice of law analysis. Please provide a complete court decision that may contain discussions of applicable law, governing law, or private international law principles."

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
- Supporting citations and precedents only when the court explicitly relies on them for their choice of law determination

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
        prompt = col_prompt.format(text=text[:8000])  # Limit text to prevent token overflow
        response = llm.invoke([
            SystemMessage(content="You are an expert in private international law and choice of law analysis. Extract relevant sections accurately and comprehensively."),
            HumanMessage(content=prompt)
        ])
        
        extracted_content = response.content.strip()
        
        if extracted_content and len(extracted_content) > 50:
            return f"**Choice of Law Section Extraction**\n\nThe following sections from the court decision discuss choice of law and private international law principles:\n\n{extracted_content}\n\n**Note:** This extraction focuses on the court's reasoning about applicable law, choice of law clauses, and PIL principles as discussed in the original judgment."
        else:
            return "**Choice of Law Extraction: No PIL Discussion Found**\n\nAfter analyzing the provided court decision, no substantial discussion of choice of law, applicable law determination, or private international law principles was identified. The case may primarily involve domestic law issues or may not contain explicit PIL analysis."
            
    except Exception as e:
        return f"**Choice of Law Extraction: Analysis Error**\n\nUnable to complete choice of law section extraction due to technical error: {str(e)}. This may be due to LLM service issues, text processing errors, or network connectivity problems. Please try again with the same or alternative text."

@tool
def classify_legal_themes(text: str = "", col_section: str = ""):
    """
    Classify legal themes based on provided themes database and case analysis.
    
    Args:
        text (str): The full court decision text
        col_section (str): The extracted choice of law section
    
    Returns:
        str: Detailed analysis with identified legal themes and explanations
    """
    if not text or len(text.strip()) < 50:
        return "**Theme Classification: Insufficient Text**\n\nThe provided text is too short to analyze for legal themes. Please provide a complete court decision that contains PIL analysis or choice of law discussions."
    
    try:
        themes = load_themes()
        if not themes:
            return "**Theme Classification: Database Error**\n\nUnable to load the themes database. The system cannot perform theme classification without access to the reference themes. Please check that the themes.csv file is properly installed."
        
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
        
        prompt = theme_prompt.format(
            text=text[:3000],  # Limit text length
            col_section=col_section[:2000] if col_section else "No specific choice of law section provided",
            themes_table=themes_table
        )
        
        # Attempt classification up to 3 times to ensure valid themes
        classified_themes = []
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
                    classified_themes = result_list
                    break
            except json.JSONDecodeError:
                # Try to extract themes from text response
                result_list = [theme.strip() for theme in response.content.split(',')]
                # Filter valid themes
                valid_results = [item for item in result_list if item in valid_theme_names]
                if valid_results:
                    classified_themes = valid_results
                    break
        
        if classified_themes:
            # Get definitions for identified themes
            theme_explanations = []
            for theme_name in classified_themes:
                for theme in themes:
                    if theme['theme'] == theme_name:
                        theme_explanations.append(f"**{theme_name}**: {theme['definition'][:200]}{'...' if len(theme['definition']) > 200 else ''}")
                        break
            
            result = f"**Theme Classification Analysis**\n\nThe following legal themes have been identified in this case:\n\n"
            result += f"**Identified Themes:** {', '.join(classified_themes)}\n\n"
            result += "**Theme Definitions:**\n" + "\n\n".join(theme_explanations)
            return result
        else:
            return "**Theme Classification: No Specific PIL Themes Identified**\n\nAfter analysis, no specific private international law themes from the reference database were clearly identified in this case. This may indicate that the case involves general PIL principles without focusing on specific themes like party autonomy, mandatory rules, or consumer contracts, or the case may primarily involve domestic legal issues."
            
    except Exception as e:
        return f"**Theme Classification: Analysis Error**\n\nUnable to complete theme classification due to technical error: {str(e)}. This may be due to LLM service issues, database access problems, or text processing errors. Please try again or provide alternative text."
        
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
        str: Comprehensive analysis of the choice of law issue in the case
    """
    if not text or len(text.strip()) < 50:
        return "**Choice of Law Issue Analysis: Insufficient Text**\n\nThe provided text is too short to analyze for choice of law issues. Please provide a complete court decision that contains PIL analysis or choice of law discussions."
    
    try:
        # Load theme definitions for context
        theme_definitions = ""
        if themes:
            themes_list = [t.strip() for t in themes.split(',')]
            all_themes = load_themes()
            if all_themes:
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
        
        prompt = issue_prompt.format(
            text=text[:3000],  # Limit text length
            col_section=col_section[:2000] if col_section else "No specific choice of law section provided",
            theme_definitions=theme_definitions if theme_definitions else "No specific themes identified"
        )
        
        response = llm.invoke([
            SystemMessage(content="You are an expert in private international law and choice of law analysis. Provide detailed analysis of PIL issues."),
            HumanMessage(content=prompt)
        ])
        
        issue_analysis = response.content.strip()
        
        if issue_analysis and len(issue_analysis) > 50:
            return f"**Choice of Law Issue Analysis**\n\n{issue_analysis}\n\n**Note:** This analysis focuses on the specific PIL challenges and choice of law determinations that the court needed to address in reaching its decision."
        else:
            return "**Choice of Law Issue Analysis: No Clear PIL Issues Identified**\n\nAfter analysis, no specific choice of law issues were clearly identified in this case. This may indicate that the case primarily involves domestic law applications, or the PIL aspects may not be explicitly discussed in the available text."
            
    except Exception as e:
        return f"**Choice of Law Issue Analysis: Analysis Error**\n\nUnable to complete choice of law issue analysis due to technical error: {str(e)}. This may be due to LLM service issues, theme database access problems, or text processing errors. Please try again."

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
        str: Comprehensive analysis of the court's position and reasoning
    """
    if not text or len(text.strip()) < 50:
        return "**Court Position Analysis: Insufficient Text**\n\nThe provided text is too short to analyze the court's position on choice of law matters. Please provide a complete court decision that contains PIL analysis and reasoning."
    
    try:
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
        
        prompt = position_prompt.format(
            text=text[:3000],  # Limit text length
            col_section=col_section[:2000] if col_section else "No specific choice of law section provided",
            themes=themes if themes else "No specific themes identified",
            col_issue=col_issue[:1000] if col_issue else "No specific choice of law issue identified"
        )
        
        response = llm.invoke([
            SystemMessage(content="You are an expert in private international law and judicial analysis. Provide thorough analysis of court reasoning."),
            HumanMessage(content=prompt)
        ])
        
        court_analysis = response.content.strip()
        
        if court_analysis and len(court_analysis) > 50:
            return f"**Court Position Analysis**\n\n{court_analysis}\n\n**Note:** This analysis examines the court's reasoning process, legal methodology, and the practical implications of its choice of law determination."
        else:
            return "**Court Position Analysis: No Clear Court Position Identified**\n\nAfter analysis, no clear court position on choice of law matters could be identified in this case. This may indicate that the case does not contain explicit PIL reasoning, or the court's position may not be clearly articulated in the available text."
            
    except Exception as e:
        return f"**Court Position Analysis: Analysis Error**\n\nUnable to complete court position analysis due to technical error: {str(e)}. This may be due to LLM service issues, input processing problems, or network connectivity issues. Please try again."

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
        return ("**Legal Case Analysis: Input Required**\n\nPlease provide the legal case details you would like me to analyze. "
                "Include relevant facts, legal issues, parties involved, jurisdiction, "
                "and any specific areas of concern.")
    
    try:
        analysis_steps = []
        
        # Step 1: Detect jurisdiction and legal system
        jurisdiction = detect_precise_jurisdiction(case_details)
        legal_system = detect_legal_system_type("", case_details)  # Let it auto-detect from text
        analysis_steps.append("✓ Jurisdiction and legal system detection completed")
        
        # Step 2: Extract choice of law sections  
        col_section = extract_choice_of_law_section(case_details)
        analysis_steps.append("✓ Choice of law section extraction completed")
        
        # Step 3: Classify themes
        themes = classify_legal_themes(case_details, col_section)
        analysis_steps.append("✓ Legal theme classification completed")
        
        # Step 4: Identify choice of law issue
        col_issue = identify_choice_of_law_issue(case_details, col_section, themes)
        analysis_steps.append("✓ Choice of law issue identification completed")
        
        # Step 5: Analyze court's position
        courts_position = analyze_courts_position(case_details, col_section, themes, col_issue)
        analysis_steps.append("✓ Court position analysis completed")
        
        # Compile comprehensive analysis
        analysis = f"""# COMPREHENSIVE LEGAL CASE ANALYSIS

## Analysis Process
{chr(10).join(analysis_steps)}

---

## JURISDICTION & LEGAL SYSTEM
{jurisdiction}

{legal_system}

---

## CHOICE OF LAW ANALYSIS
{col_section}

---

## LEGAL THEMES CLASSIFICATION
{themes}

---

## CHOICE OF LAW ISSUE IDENTIFICATION
{col_issue}

---

## COURT'S POSITION ANALYSIS
{courts_position}

---

## SUMMARY & RECOMMENDATIONS

**Key Insights:**
- This comprehensive analysis utilized advanced PIL analysis tools
- Each component was analyzed using specialized legal expertise models
- The analysis follows established private international law methodologies

**Recommendations:**
- Consider the court's reasoning for future similar cases
- Review the applicable PIL principles identified
- Analyze the practical implications of the chosen law
- Use this analysis for academic research or case preparation
- Consult qualified legal professionals for case-specific legal advice

**Important Note:** This analysis is for educational and research purposes. Please consult with qualified legal professionals for actual legal matters and case-specific advice."""

        return analysis
        
    except Exception as e:
        return f"**Comprehensive Legal Case Analysis: System Error**\n\nUnable to complete comprehensive analysis due to technical error: {str(e)}. This may be due to LLM service issues, database problems, or processing errors. Please try again or contact support if the issue persists."

@tool
def welcome_user():
    """
    Welcome the user to the Legal Case Analyzer toolset.
    
    Returns:
        str: A welcome message with available capabilities.
    """
    return ("**Welcome to the Legal Case Analyzer!** 🏛️\n\nYou have access to advanced private international law analysis tools:\n\n"
            "**🔍 Analysis Capabilities:**\n"
            "- Jurisdiction detection and legal system classification\n"
            "- Choice of law section extraction from court decisions\n"
            "- Legal theme classification (Party autonomy, Mandatory rules, etc.)\n"
            "- Choice of law issue identification\n"
            "- Court position and reasoning analysis\n"
            "- Comprehensive PIL case analysis\n\n"
            "**📚 Supported Features:**\n"
            "- 249+ jurisdictions worldwide\n"
            "- 12 specialized PIL themes\n"
            "- Civil-law and Common-law system analysis\n"
            "- Multi-step analytical workflow\n\n"
            "Please provide your legal case details to get started with the analysis!")

@tool
def search_legal_precedents(query: str = ""):
    """
    Search for legal precedents related to a query with PIL focus.
    
    Args:
        query (str): The search query for finding relevant legal precedents.
                    Include key legal concepts, issues, or case types.
    
    Returns:
        str: Analysis of relevant legal concepts and guidance for precedent research.
    """
    if not query or query.strip() == "":
        return "**Legal Precedent Search: Query Required**\n\nPlease provide a search query to find relevant legal precedents. Include key legal concepts, PIL themes, jurisdictions, or specific choice of law issues you're researching."
    
    try:
        # Analyze the query to provide targeted guidance
        search_guidance = f"""**Legal Precedent Search Analysis for: "{query}"**

**🔍 Search Strategy Recommendations:**

**Primary Research Areas:**
- Case law databases for jurisdiction-specific precedents
- International court decisions (ICJ, PCIJ, regional courts)
- National supreme court decisions on PIL matters
- Arbitral awards from major arbitration centers

**Suggested Keywords for Database Search:**
- Core PIL terms from your query
- Related jurisdiction names and legal systems
- Applicable treaties and conventions
- Specific legal principles identified

**PIL-Specific Resources to Consult:**
- Hague Conference case law database
- Conflict of Laws digests and reporters  
- International legal materials collections
- Academic PIL casebooks and commentaries

**Analysis Approach:**
1. Search for cases with similar factual patterns
2. Look for decisions applying similar PIL principles
3. Compare reasoning across different jurisdictions
4. Identify trends in judicial interpretation

**⚠️ Important Notes:**
- This tool provides research guidance rather than actual case retrieval
- Access legal databases like Westlaw, LexisNexis, or jurisdiction-specific systems
- Consider consulting PIL practitioners or academic specialists
- Verify current validity and authority of located precedents

**Next Steps:**
Use the jurisdiction detection and theme classification tools to analyze any precedents you find, enabling comparative analysis of different courts' approaches to similar PIL issues."""

        return search_guidance
        
    except Exception as e:
        return f"**Legal Precedent Search: Analysis Error**\n\nUnable to provide search guidance due to technical error: {str(e)}. Please try again with a refined search query."


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
