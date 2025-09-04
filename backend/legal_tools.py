"""
Professional Legal Analysis Tools
Adapted from the reference Streamlit implementation
"""

import json
import re
import time
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

# LLM will be initialized when needed
llm = None

def get_llm():
    """Get or initialize the LLM instance"""
    global llm
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    return llm

# ========== JURISDICTION DETECTION ==========

class JurisdictionDetector:
    """Advanced jurisdiction detection with mapping and LLM fallback"""
    
    @staticmethod
    def get_jurisdiction_mapping() -> Dict[str, str]:
        """Mapping of jurisdictions to legal system types"""
        civil_law = {
            'switzerland', 'germany', 'france', 'italy', 'spain', 'austria', 'netherlands', 'belgium',
            'luxembourg', 'portugal', 'greece', 'finland', 'sweden', 'denmark', 'norway', 'poland',
            'czech republic', 'slovakia', 'hungary', 'romania', 'bulgaria', 'croatia', 'slovenia',
            'estonia', 'latvia', 'lithuania', 'malta', 'cyprus', 'japan', 'south korea', 'china',
            'taiwan', 'brazil', 'argentina', 'mexico', 'chile', 'colombia', 'peru', 'ecuador',
            'bolivia', 'paraguay', 'uruguay', 'venezuela', 'russia', 'ukraine', 'turkey', 'egypt',
            'morocco', 'tunisia', 'algeria', 'iran', 'lebanon', 'jordan', 'qatar', 'kuwait', 'bahrain',
            'uae', 'saudi arabia', 'israel', 'indonesia', 'thailand', 'vietnam', 'cambodia', 'laos',
            'ethiopia', 'angola', 'mozambique', 'kazakhstan', 'uzbekistan', 'tajikistan', 'kyrgyzstan',
            'belarus', 'moldova', 'georgia', 'armenia', 'azerbaijan', 'albania', 'bosnia and herzegovina',
            'north macedonia', 'montenegro', 'serbia', 'kosovo', 'iceland', 'liechtenstein', 'monaco',
            'san marino', 'andorra', 'european union', 'ohada'
        }
        
        common_law = {
            'united states', 'usa', 'united kingdom', 'england', 'scotland', 'wales', 'northern ireland',
            'ireland', 'canada', 'australia', 'new zealand', 'india', 'pakistan', 'bangladesh',
            'sri lanka', 'malaysia', 'singapore', 'hong kong', 'south africa', 'nigeria', 'ghana',
            'kenya', 'uganda', 'tanzania', 'zambia', 'zimbabwe', 'botswana', 'malawi', 'sierra leone',
            'gambia', 'jamaica', 'barbados', 'trinidad and tobago', 'bahamas', 'belize', 'guyana',
            'philippines', 'myanmar'
        }
        
        mapping = {}
        for jurisdiction in civil_law:
            mapping[jurisdiction] = 'Civil-law jurisdiction'
        for jurisdiction in common_law:
            mapping[jurisdiction] = 'Common-law jurisdiction'
        
        return mapping
    
    @classmethod
    def detect_by_name(cls, jurisdiction_name: str) -> Optional[str]:
        """Detect jurisdiction type by name"""
        if not jurisdiction_name or jurisdiction_name.lower() in ['unknown', 'n/a', 'none']:
            return None
        
        mapping = cls.get_jurisdiction_mapping()
        jurisdiction_lower = jurisdiction_name.lower()
        
        # Direct lookup
        if jurisdiction_lower in mapping:
            return mapping[jurisdiction_lower]
        
        # Partial match
        for mapped_jurisdiction, legal_system in mapping.items():
            if mapped_jurisdiction in jurisdiction_lower or jurisdiction_lower in mapped_jurisdiction:
                return legal_system
        
        return None
    
    @classmethod
    def detect_by_llm(cls, jurisdiction_name: str, text: str) -> str:
        """LLM-based jurisdiction detection"""
        prompt = f"""
        Analyze this court decision text and classify it as one of:
        - 'Civil-law jurisdiction'
        - 'Common-law jurisdiction' 
        - 'No court decision'
        
        Consider the jurisdiction: {jurisdiction_name}
        
        Look for indicators such as:
        - Legal citation formats
        - Court structure and naming
        - Legal reasoning style
        - Precedent usage
        - Statutory interpretation approach
        
        Court Decision Text:
        {text[:2000]}...
        
        Classification:
        """
        
        response = get_llm().invoke([
            SystemMessage(content="You are an expert in comparative legal systems."),
            HumanMessage(content=prompt)
        ])
        
        result = response.content.strip()
        allowed = ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"]
        
        for option in allowed:
            if option.lower() in result.lower():
                return option
        
        return "No court decision"
    
    @classmethod
    def detect(cls, jurisdiction_name: str, text: str) -> Dict[str, str]:
        """Main detection method with fallback"""
        if not text or len(text.strip()) < 50:
            return {
                "jurisdiction_type": "No court decision",
                "precise_jurisdiction": jurisdiction_name or "Unknown",
                "confidence": "high",
                "method": "text_length"
            }
        
        # Try name-based detection first
        name_result = cls.detect_by_name(jurisdiction_name)
        if name_result:
            return {
                "jurisdiction_type": name_result,
                "precise_jurisdiction": jurisdiction_name,
                "confidence": "high",
                "method": "name_mapping"
            }
        
        # Fallback to LLM
        llm_result = cls.detect_by_llm(jurisdiction_name, text)
        return {
            "jurisdiction_type": llm_result,
            "precise_jurisdiction": jurisdiction_name or "Unknown",
            "confidence": "medium",
            "method": "llm_analysis"
        }

# ========== CHOICE OF LAW EXTRACTOR ==========

class ChoiceOfLawExtractor:
    """Extract Choice of Law sections from court decisions"""
    
    @staticmethod
    def extract(text: str, jurisdiction_type: str = "Civil-law jurisdiction") -> str:
        """Extract COL section using jurisdiction-specific prompts"""
        
        if jurisdiction_type == "Civil-law jurisdiction":
            prompt = """
            Extract the sections of this court decision that deal with choice of law, conflict of laws, 
            or private international law. Focus on:
            
            1. Discussion of applicable law determination
            2. Analysis of connecting factors
            3. Application of PIL provisions/articles
            4. Choice of law methodology
            5. Conflict rules application
            
            Exclude purely procedural or jurisdictional discussions.
            
            Court Decision:
            {text}
            
            Extracted Choice of Law Section:
            """
        else:  # Common law
            prompt = """
            Extract the sections dealing with choice of law, conflicts of law, or determining applicable law.
            Focus on:
            
            1. Choice of law analysis and rules
            2. Most significant relationship test
            3. Party autonomy in law selection
            4. Conflicts principles and precedents
            5. Foreign law application
            
            Court Decision:
            {text}
            
            Extracted Choice of Law Section:
            """
        
        response = get_llm().invoke([
            SystemMessage(content=f"You are an expert in {jurisdiction_type} choice of law analysis."),
            HumanMessage(content=prompt.format(text=text))
        ])
        
        return response.content.strip()

# ========== THEME CLASSIFIER ==========

class ThemeClassifier:
    """Classify PIL themes in court decisions"""
    
    # Sample themes - in production this would be loaded from CSV
    VALID_THEMES = [
        "Choice of Law Clauses",
        "Contractual Obligations",
        "Cross-border Transactions", 
        "Party Autonomy",
        "Connecting Factors",
        "Most Significant Relationship",
        "Mandatory Rules",
        "Public Policy",
        "Renvoi",
        "Characterization",
        "Tort Law",
        "Property Rights",
        "Family Law",
        "Succession Law",
        "Corporate Law",
        "Consumer Protection",
        "Employment Law",
        "Intellectual Property",
        "International Arbitration",
        "Recognition and Enforcement"
    ]
    
    @classmethod
    def classify(cls, text: str, col_section: str, jurisdiction_type: str) -> List[str]:
        """Classify PIL themes with validation"""
        
        themes_list = ", ".join(cls.VALID_THEMES)
        
        prompt = f"""
        Classify the private international law themes present in this court decision.
        
        Available themes: {themes_list}
        
        Instructions:
        1. Identify the main PIL themes discussed in the case
        2. Return as a JSON list of theme names
        3. Only use themes from the provided list
        4. Focus on themes relevant to choice of law analysis
        
        Jurisdiction: {jurisdiction_type}
        
        Full Text: {text[:1500]}...
        
        Choice of Law Section: {col_section}
        
        Return only the JSON list:
        """
        
        max_attempts = 3
        for attempt in range(max_attempts):
            response = get_llm().invoke([
                SystemMessage(content="You are an expert in private international law classification."),
                HumanMessage(content=prompt)
            ])
            
            try:
                # Try to parse as JSON
                themes = json.loads(response.content.strip())
                if isinstance(themes, list):
                    # Validate themes
                    valid_themes = [theme for theme in themes if theme in cls.VALID_THEMES]
                    if valid_themes:
                        return valid_themes
            except json.JSONDecodeError:
                # Try to extract themes from text response
                themes = []
                for theme in cls.VALID_THEMES:
                    if theme.lower() in response.content.lower():
                        themes.append(theme)
                if themes:
                    return themes
        
        # Fallback
        return ["Cross-border Transactions"]

# ========== CASE ANALYZER ==========

class CaseAnalyzer:
    """Main case analysis functions"""
    
    @staticmethod
    def analyze_relevant_facts(text: str, col_section: str, jurisdiction_type: str) -> str:
        """Extract relevant facts for choice of law analysis"""
        
        prompt = f"""
        Extract and synthesize factual elements essential for understanding the choice of law analysis.
        
        Requirements:
        1. Maximum 300 words in narrative form
        2. Focus on: party characteristics, transaction geography, choice of law indicators
        3. Include: connecting factors, international elements, conflict triggers
        4. Exclude: specific amounts, exact dates, procedural details
        5. Use flowing, connected sentences
        
        Jurisdiction: {jurisdiction_type}
        
        Court Decision Text: {text}
        
        Choice of Law Section: {col_section}
        
        Relevant Facts:
        """
        
        response = get_llm().invoke([
            SystemMessage(content=f"You are a legal analyst specializing in {jurisdiction_type} choice of law."),
            HumanMessage(content=prompt)
        ])
        
        return response.content.strip()
    
    @staticmethod
    def identify_pil_provisions(text: str, col_section: str, jurisdiction_type: str) -> List[str]:
        """Extract PIL provisions cited in the decision"""
        
        prompt = f"""
        Extract private international law provisions cited in this court decision.
        
        Instructions:
        1. Look for articles, sections, or provisions of PIL legislation
        2. Include international treaties and conventions
        3. Format as: ["Article number, abbreviated instrument name"]
        4. Return JSON list only
        5. If none found, return ["NA"]
        
        Examples:
        - Switzerland: ["Art. 187, PILA"]
        - EU: ["Art. 3, Rome I Regulation"]
        - US: ["Restatement (Second) Conflict of Laws § 187"]
        
        Jurisdiction: {jurisdiction_type}
        
        Court Decision: {text}
        
        COL Section: {col_section}
        
        PIL Provisions (JSON):
        """
        
        response = get_llm().invoke([
            SystemMessage(content="You are an expert in PIL provision identification."),
            HumanMessage(content=prompt)
        ])
        
        try:
            provisions = json.loads(response.content.strip())
            return provisions if isinstance(provisions, list) else ["NA"]
        except json.JSONDecodeError:
            return ["NA"]
    
    @staticmethod
    def identify_col_issue(text: str, col_section: str, themes: List[str], jurisdiction_type: str) -> str:
        """Identify the main choice of law issue"""
        
        themes_str = ", ".join(themes)
        
        prompt = f"""
        Identify the main private international law issue as a concise question.
        
        The issue should:
        1. Be phrased as a general legal question
        2. Focus on choice of law methodology
        3. Be applicable beyond this specific case
        4. Relate to the identified themes: {themes_str}
        
        Examples:
        - "Can parties validly choose the law of a country with no connection to their contract?"
        - "Does the closest connection test apply when parties made no express choice of law?"
        - "Can an implied choice of law be inferred from forum selection clauses?"
        
        Jurisdiction: {jurisdiction_type}
        
        Court Decision: {text}
        
        COL Section: {col_section}
        
        The choice of law issue is:
        """
        
        response = get_llm().invoke([
            SystemMessage(content="You are an expert in choice of law issue identification."),
            HumanMessage(content=prompt)
        ])
        
        return response.content.strip()
    
    @staticmethod
    def analyze_courts_position(text: str, col_section: str, col_issue: str, themes: List[str], jurisdiction_type: str) -> str:
        """Analyze the court's position on the choice of law issue"""
        
        themes_str = ", ".join(themes)
        
        prompt = f"""
        Summarize the court's position on the choice-of-law issue in a general way.
        
        Requirements:
        1. Answer the specific issue: {col_issue}
        2. Generalize for application to other PIL cases
        3. Maximum 300 words
        4. Neutral and objective tone
        5. Focus on legal principle established
        
        Context:
        - Jurisdiction: {jurisdiction_type}
        - Themes: {themes_str}
        - Issue: {col_issue}
        
        Court Decision: {text}
        
        COL Section: {col_section}
        
        The court's position is:
        """
        
        response = get_llm().invoke([
            SystemMessage(content="You are an expert in legal position analysis."),
            HumanMessage(content=prompt)
        ])
        
        return response.content.strip()
    
    @staticmethod
    def extract_obiter_dicta(text: str, col_section: str, jurisdiction_type: str) -> str:
        """Extract obiter dicta from common law decisions"""
        
        if jurisdiction_type != "Common-law jurisdiction":
            return "N/A - Not applicable for civil law jurisdiction"
        
        prompt = f"""
        Extract obiter dicta (non-binding judicial observations) from this common law decision.
        
        Focus on:
        1. Judicial comments not essential to the decision
        2. Hypothetical scenarios discussed
        3. Broader principles mentioned
        4. Future application considerations
        
        Court Decision: {text}
        
        COL Section: {col_section}
        
        Obiter Dicta:
        """
        
        response = get_llm().invoke([
            SystemMessage(content="You are an expert in common law judicial analysis."),
            HumanMessage(content=prompt)
        ])
        
        return response.content.strip()
    
    @staticmethod
    def extract_dissenting_opinions(text: str, col_section: str, jurisdiction_type: str) -> str:
        """Extract dissenting opinions from common law decisions"""
        
        if jurisdiction_type != "Common-law jurisdiction":
            return "N/A - Not applicable for civil law jurisdiction"
        
        prompt = f"""
        Extract dissenting opinions from this common law decision.
        
        Focus on:
        1. Alternative legal reasoning
        2. Different choice of law approaches
        3. Criticism of majority position
        4. Alternative precedent interpretation
        
        Court Decision: {text}
        
        COL Section: {col_section}
        
        Dissenting Opinions:
        """
        
        response = get_llm().invoke([
            SystemMessage(content="You are an expert in common law judicial analysis."),
            HumanMessage(content=prompt)
        ])
        
        return response.content.strip()
    
    @staticmethod
    def generate_abstract(case_data: Dict[str, Any]) -> str:
        """Generate comprehensive case abstract"""
        
        prompt = f"""
        Create a concise abstract summarizing this PIL case's choice of law analysis.
        
        Requirements:
        1. One paragraph maximum
        2. Begin with factual context
        3. Progress through legal question and reasoning
        4. Conclude with precedential principle
        5. Maximum 300 words
        6. Professional legal research language
        
        Case Information:
        - Jurisdiction: {case_data.get('jurisdiction', 'Unknown')}
        - Themes: {case_data.get('classification', [])}
        - Facts: {case_data.get('relevant_facts', '')}
        - PIL Provisions: {case_data.get('pil_provisions', [])}
        - COL Issue: {case_data.get('col_issue', '')}
        - Court's Position: {case_data.get('courts_position', '')}
        
        Abstract:
        """
        
        response = get_llm().invoke([
            SystemMessage(content="You are an expert legal researcher creating case abstracts."),
            HumanMessage(content=prompt)
        ])
        
        return response.content.strip()

# Export main classes
__all__ = [
    'JurisdictionDetector',
    'ChoiceOfLawExtractor', 
    'ThemeClassifier',
    'CaseAnalyzer'
]
