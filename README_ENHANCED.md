# Legal Case Analyzer - Professional Edition

## Overview

The Legal Case Analyzer has been enhanced with professional-grade legal analysis tools based on the SLOP (Simple Legal Operations Platform) architecture. This version provides sophisticated Private International Law (PIL) and Choice of Law (COL) analysis capabilities.

## 🚀 Key Features

### Professional Legal Analysis Tools
- **Jurisdiction Detection**: Advanced detection of legal system types (Civil Law vs Common Law)
- **Choice of Law Extraction**: Sophisticated extraction of COL sections from court decisions
- **Theme Classification**: Automated classification of PIL themes using validated taxonomies
- **Fact Analysis**: Extraction and synthesis of legally relevant facts
- **PIL Provision Identification**: Recognition of cited private international law provisions
- **Issue Identification**: Formulation of precise choice of law questions
- **Court Position Analysis**: Analysis of judicial reasoning and holdings
- **Common Law Specific Features**: Obiter dicta and dissenting opinion extraction
- **Abstract Generation**: Comprehensive case abstracts for legal research

### Multi-Pattern Analysis Workflows
- **Quick Analysis**: Basic jurisdiction detection and theme classification
- **Sequential**: Step-by-step analysis workflow
- **Parallel**: Multiple analysis perspectives simultaneously  
- **Comprehensive**: Complete PIL/COL analysis pipeline

### Streaming & Interactive Features
- **Real-time Streaming**: Token-by-token response streaming
- **Contextual Chat**: Legal Q&A with case analysis context
- **Session Management**: Persistent analysis states across interactions
- **Export Capabilities**: Complete analysis export in structured format

## 🏗️ Architecture

### SLOP-Based Design
The API follows the SLOP (Simple Legal Operations Platform) architecture with:
- **Specialized Agents**: Dedicated tools for each analysis aspect
- **Router System**: Intelligent routing to appropriate analysis methods
- **Pattern Support**: Multiple workflow patterns for different use cases
- **Memory Management**: Persistent state and conversation history

### Legal Analysis Pipeline
```
Court Decision Input
      ↓
Jurisdiction Detection → Legal System Classification
      ↓
COL Section Extraction → Relevant Text Identification  
      ↓
Theme Classification → PIL Theme Identification
      ↓
Multi-Step Analysis:
  • Relevant Facts
  • PIL Provisions  
  • COL Issues
  • Court's Position
  • [Common Law: Obiter Dicta, Dissenting Opinions]
      ↓
Abstract Generation → Research-Ready Summary
```

## 📡 API Endpoints

### Core Analysis
```bash
POST /analyze
```
**Request:**
```json
{
  "case_citation": "BGH, Urteil vom 15.12.2020 - XI ZR 234/19",
  "full_text": "Court decision text...",
  "session_id": "session-123",
  "pattern": "comprehensive",
  "target_stage": "complete"
}
```

**Response:**
```json
{
  "session_id": "session-123",
  "stage": "complete",
  "jurisdiction": "Civil-law jurisdiction",
  "completion_percentage": 100.0,
  "result": {
    "jurisdiction": "Civil-law jurisdiction",
    "precise_jurisdiction": "Germany",
    "classification": ["Choice of Law Clauses", "Party Autonomy"],
    "col_section": ["Extracted COL text..."],
    "relevant_facts": ["Synthesized facts..."],
    "pil_provisions": ["Art. 187, PILA"],
    "col_issue": ["Can parties choose law without connection?"],
    "courts_position": ["Court's analysis..."],
    "abstract": ["Case summary..."]
  }
}
```

### Streaming Legal Chat
```bash
POST /chat/stream
```
Real-time legal Q&A with case context awareness.

### Tool Information
```bash
GET /tools
```
Lists available analysis tools, patterns, and supported jurisdictions.

### Session Management
```bash
GET /sessions              # List all sessions
DELETE /sessions/{id}      # Clear specific session  
GET /sessions/{id}/export  # Export complete analysis
```

## 🔧 Professional Tools

### JurisdictionDetector
- **Mapping-Based Detection**: 100+ jurisdiction mappings to legal systems
- **LLM Fallback**: Intelligent analysis for unknown jurisdictions
- **Confidence Scoring**: Reliability assessment of classification

### ChoiceOfLawExtractor  
- **Jurisdiction-Specific Prompts**: Tailored extraction for Civil vs Common Law
- **Contextual Analysis**: Focus on PIL methodology and reasoning
- **Quality Filtering**: Exclusion of procedural/non-relevant content

### ThemeClassifier
- **Validated Taxonomy**: 20+ PIL themes with legal definitions
- **Multi-Attempt Validation**: Ensures theme accuracy and completeness
- **JSON Response Parsing**: Structured theme classification

### CaseAnalyzer
- **Fact Synthesis**: 300-word narrative fact summaries
- **PIL Provision Recognition**: Automated citation extraction and formatting
- **Issue Formulation**: General legal questions from specific cases
- **Position Analysis**: Court reasoning and precedential value
- **Abstract Generation**: Research-ready case summaries

## 📋 Analysis Patterns

### Quick Analysis
- Jurisdiction detection
- Basic theme classification
- ~30 seconds processing

### Comprehensive Analysis  
- Full 8-10 step pipeline
- All analysis components
- 2-3 minutes processing

### Sequential Analysis
- Step-by-step workflow
- User validation at each stage
- Interactive analysis

### Parallel Analysis
- Multiple perspective analysis
- Comparative legal reasoning
- Enhanced insight generation

## 🚀 Getting Started

### Installation
```bash
cd backend
pip install -r requirements.txt
```

### Environment Setup
```bash
# Create .env file
OPENAI_API_KEY=your_api_key_here
```

### Running the Enhanced API
```bash
python main_enhanced.py
```

### Testing
```bash
python test_enhanced_api.py
```

## 📚 Legal Accuracy

### Jurisdiction Coverage
- **Civil Law**: 50+ jurisdictions including EU, Germany, Switzerland, France
- **Common Law**: 25+ jurisdictions including US, UK, Australia, Canada
- **Mixed Systems**: Recognition and appropriate analysis methods

### PIL Expertise
- Choice of law methodology
- Connecting factors analysis
- Party autonomy principles
- Mandatory rules and public policy
- Cross-border transaction analysis
- International treaty recognition

### Quality Assurance
- Validated legal theme taxonomies
- Professional citation formatting
- Precedent-aware analysis
- Research-grade abstracts

## 🔄 Workflow Integration

### Legal Research
- Case analysis for academic research
- Precedent identification and synthesis
- Comparative law analysis
- PIL methodology documentation

### Practice Applications  
- Client case analysis
- Choice of law strategy development
- Cross-border transaction planning
- Conflict of laws research

### Educational Use
- Law school case studies
- PIL concept illustration
- Jurisdiction comparison
- Legal reasoning analysis

## 🛠️ Technical Specifications

### Performance
- **Analysis Speed**: 30 seconds - 3 minutes depending on pattern
- **Streaming Latency**: <100ms token response time
- **Session Persistence**: Full analysis state management
- **Export Formats**: JSON, structured legal data

### Scalability
- Session-based architecture
- Stateless analysis tools
- Horizontal scaling support
- Database integration ready

### Integration
- RESTful API design
- OpenAPI documentation
- WebSocket streaming support
- Frontend framework agnostic

## 📖 Legal Disclaimer

This tool provides AI-assisted legal analysis for research and educational purposes. It does not constitute legal advice and should not replace consultation with qualified legal professionals. Users should verify all analysis results and citations independently.

## 🤝 Contributing

Based on the CoLD (Conflict of Laws Database) project methodology and the SLOP architecture. Contributions welcome for:
- Additional jurisdiction mappings
- Enhanced PIL provision recognition
- Extended theme taxonomies
- Improved analysis accuracy

## 📞 Support

For technical support, legal accuracy improvements, or feature requests, please refer to the project documentation and issue tracking system.
