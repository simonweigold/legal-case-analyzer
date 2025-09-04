"""
Legal Case Analyzer API - Enhanced with Professional Tools
Based on SLOP architecture with specialized legal analysis agents
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LegalAnalyzer")

from dotenv import find_dotenv, load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Import professional legal tools
from legal_tools import JurisdictionDetector, ChoiceOfLawExtractor, ThemeClassifier, CaseAnalyzer

# Load environment variables
load_dotenv(find_dotenv())

# ========== ENUMS AND DATA CLASSES ==========

class JurisdictionType(str, Enum):
    CIVIL_LAW = "Civil-law jurisdiction"
    COMMON_LAW = "Common-law jurisdiction"
    NO_COURT_DECISION = "No court decision"

class AnalysisPattern(str, Enum):
    SEQUENTIAL = "sequential"  # Extract → Classify → Analyze → Abstract
    PARALLEL = "parallel"     # Multiple analysis perspectives
    COMPREHENSIVE = "comprehensive"  # Full workflow with all steps
    QUICK = "quick"          # Basic analysis only

class AnalysisStage(str, Enum):
    JURISDICTION_DETECTION = "jurisdiction_detection"
    COL_EXTRACTION = "col_extraction" 
    THEME_CLASSIFICATION = "theme_classification"
    FACT_ANALYSIS = "fact_analysis"
    PIL_PROVISIONS = "pil_provisions"
    COL_ISSUE = "col_issue"
    COURTS_POSITION = "courts_position"
    OBITER_DICTA = "obiter_dicta"
    DISSENTING_OPINIONS = "dissenting_opinions"
    ABSTRACT = "abstract"
    COMPLETE = "complete"

@dataclass
class AnalysisState:
    """Enhanced state management for legal case analysis"""
    session_id: str
    case_citation: str
    full_text: str
    jurisdiction: Optional[JurisdictionType] = None
    precise_jurisdiction: Optional[str] = None
    col_section: List[str] = None
    classification: List[str] = None
    relevant_facts: List[str] = None
    pil_provisions: List[str] = None
    col_issue: List[str] = None
    courts_position: List[str] = None
    obiter_dicta: List[str] = None
    dissenting_opinions: List[str] = None
    abstract: List[str] = None
    analysis_stage: AnalysisStage = AnalysisStage.JURISDICTION_DETECTION
    chat_history: List[tuple] = None
    analysis_done: bool = False
    
    def __post_init__(self):
        if self.col_section is None:
            self.col_section = []
        if self.classification is None:
            self.classification = []
        if self.relevant_facts is None:
            self.relevant_facts = []
        if self.pil_provisions is None:
            self.pil_provisions = []
        if self.col_issue is None:
            self.col_issue = []
        if self.courts_position is None:
            self.courts_position = []
        if self.obiter_dicta is None:
            self.obiter_dicta = []
        if self.dissenting_opinions is None:
            self.dissenting_opinions = []
        if self.abstract is None:
            self.abstract = []
        if self.chat_history is None:
            self.chat_history = []

# ========== PYDANTIC MODELS ==========

class LegalCaseRequest(BaseModel):
    case_citation: str = Field(..., description="Citation of the legal case")
    full_text: str = Field(..., description="Full text of the court decision")
    session_id: str = Field(default="default", description="Session identifier")
    pattern: Optional[AnalysisPattern] = Field(default=AnalysisPattern.COMPREHENSIVE)
    target_stage: Optional[AnalysisStage] = Field(default=AnalysisStage.COMPLETE)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    context: Optional[Dict[str, Any]] = None

class StreamChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    context: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    session_id: str
    stage: AnalysisStage
    result: Dict[str, Any]
    jurisdiction: Optional[JurisdictionType] = None
    completion_percentage: float = 0.0
    next_stage: Optional[AnalysisStage] = None

class LegalToolResponse(BaseModel):
    tool_name: str
    result: Union[str, List[str], Dict[str, Any]]
    execution_time: float
    session_id: str

# ========== LEGAL ANALYSIS TOOLS ==========

@tool
def detect_jurisdiction(case_text: str, case_citation: str = "") -> Dict[str, str]:
    """
    Detect the legal system type and precise jurisdiction from a court decision.
    Returns jurisdiction type and specific jurisdiction information.
    """
    return JurisdictionDetector.detect(case_citation, case_text)

@tool
def extract_col_section(case_text: str, jurisdiction_type: str = "Civil-law jurisdiction") -> str:
    """
    Extract the Choice of Law (COL) section from a court decision.
    """
    return ChoiceOfLawExtractor.extract(case_text, jurisdiction_type)

@tool
def classify_themes(case_text: str, col_section: str, jurisdiction_type: str) -> List[str]:
    """
    Classify the private international law themes present in the case.
    """
    return ThemeClassifier.classify(case_text, col_section, jurisdiction_type)

@tool
def analyze_relevant_facts(case_text: str, col_section: str, jurisdiction_type: str) -> str:
    """
    Extract and synthesize factual elements essential for choice of law analysis.
    """
    return CaseAnalyzer.analyze_relevant_facts(case_text, col_section, jurisdiction_type)

@tool
def identify_pil_provisions(case_text: str, col_section: str, jurisdiction_type: str) -> List[str]:
    """
    Extract private international law provisions cited in the decision.
    """
    return CaseAnalyzer.identify_pil_provisions(case_text, col_section, jurisdiction_type)

@tool
def identify_col_issue(case_text: str, col_section: str, themes: List[str], jurisdiction_type: str) -> str:
    """
    Identify the main choice of law issue as a concise question.
    """
    return CaseAnalyzer.identify_col_issue(case_text, col_section, themes, jurisdiction_type)

@tool
def analyze_courts_position(case_text: str, col_section: str, col_issue: str, themes: List[str], jurisdiction_type: str) -> str:
    """
    Summarize the court's position on the choice of law issue.
    """
    return CaseAnalyzer.analyze_courts_position(case_text, col_section, col_issue, themes, jurisdiction_type)

@tool
def extract_obiter_dicta(case_text: str, col_section: str, jurisdiction_type: str) -> str:
    """
    Extract obiter dicta (non-binding judicial observations) from common law decisions.
    """
    return CaseAnalyzer.extract_obiter_dicta(case_text, col_section, jurisdiction_type)

@tool
def extract_dissenting_opinions(case_text: str, col_section: str, jurisdiction_type: str) -> str:
    """
    Extract dissenting opinions from common law decisions.
    """
    return CaseAnalyzer.extract_dissenting_opinions(case_text, col_section, jurisdiction_type)

@tool
def generate_abstract(case_data: Dict[str, Any]) -> str:
    """
    Generate a comprehensive abstract of the PIL case analysis.
    """
    return CaseAnalyzer.generate_abstract(case_data)

# ========== AGENT SYSTEM ==========

class LegalAnalysisOrchestrator:
    """Orchestrates the legal case analysis workflow"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.tools = {
            "detect_jurisdiction": detect_jurisdiction,
            "extract_col_section": extract_col_section,
            "classify_themes": classify_themes,
            "analyze_relevant_facts": analyze_relevant_facts,
            "identify_pil_provisions": identify_pil_provisions,
            "identify_col_issue": identify_col_issue,
            "analyze_courts_position": analyze_courts_position,
            "extract_obiter_dicta": extract_obiter_dicta,
            "extract_dissenting_opinions": extract_dissenting_opinions,
            "generate_abstract": generate_abstract
        }
    
    def get_analysis_pipeline(self, jurisdiction_type: JurisdictionType) -> List[str]:
        """Get the analysis pipeline based on jurisdiction type"""
        base_pipeline = [
            "detect_jurisdiction",
            "extract_col_section", 
            "classify_themes",
            "analyze_relevant_facts",
            "identify_pil_provisions",
            "identify_col_issue",
            "analyze_courts_position"
        ]
        
        if jurisdiction_type == JurisdictionType.COMMON_LAW:
            base_pipeline.extend([
                "extract_obiter_dicta",
                "extract_dissenting_opinions"
            ])
        
        base_pipeline.append("generate_abstract")
        return base_pipeline
    
    async def execute_step(self, step_name: str, state: AnalysisState) -> Dict[str, Any]:
        """Execute a single analysis step with comprehensive logging"""
        tool_func = self.tools.get(step_name)
        if not tool_func:
            raise ValueError(f"Unknown analysis step: {step_name}")
        
        logger.info(f"🔧 Executing tool: {step_name} for session: {state.session_id}")
        start_time = time.time()
        
        # Log tool execution start
        execution_entry = {
            "session_id": state.session_id,
            "tool_name": step_name,
            "start_time": start_time,
            "status": "started",
            "jurisdiction": state.jurisdiction.value if state.jurisdiction else None
        }
        
        # Add to global log
        tool_execution_log.append(execution_entry)
        
        # Add to session-specific log
        if state.session_id not in session_activity_log:
            session_activity_log[state.session_id] = []
        session_activity_log[state.session_id].append(execution_entry.copy())
        
        try:
            # Prepare arguments based on the step
            if step_name == "detect_jurisdiction":
                logger.info(f"📍 Detecting jurisdiction for case: {state.case_citation}")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "case_citation": state.case_citation
                })
                logger.info(f"✅ Jurisdiction detected: {result.get('jurisdiction_type')} ({result.get('method')})")
                
            elif step_name == "extract_col_section":
                logger.info(f"⚖️ Extracting COL section for {state.jurisdiction}")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "jurisdiction_type": state.jurisdiction.value if state.jurisdiction else "Civil-law jurisdiction"
                })
                logger.info(f"✅ COL section extracted: {len(result)} characters")
                
            elif step_name == "classify_themes":
                col_section = state.col_section[-1] if state.col_section else ""
                logger.info(f"🏷️ Classifying PIL themes...")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "col_section": col_section,
                    "jurisdiction_type": state.jurisdiction.value if state.jurisdiction else "Civil-law jurisdiction"
                })
                logger.info(f"✅ Themes classified: {result}")
                
            elif step_name == "analyze_relevant_facts":
                col_section = state.col_section[-1] if state.col_section else ""
                logger.info(f"📋 Analyzing relevant facts...")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "col_section": col_section,
                    "jurisdiction_type": state.jurisdiction.value if state.jurisdiction else "Civil-law jurisdiction"
                })
                logger.info(f"✅ Facts analyzed: {len(result)} characters")
                
            elif step_name == "identify_pil_provisions":
                col_section = state.col_section[-1] if state.col_section else ""
                logger.info(f"📖 Identifying PIL provisions...")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "col_section": col_section,
                    "jurisdiction_type": state.jurisdiction.value if state.jurisdiction else "Civil-law jurisdiction"
                })
                logger.info(f"✅ PIL provisions identified: {result}")
                
            elif step_name == "identify_col_issue":
                col_section = state.col_section[-1] if state.col_section else ""
                themes = state.classification[-1].split(", ") if state.classification else []
                logger.info(f"❓ Identifying COL issue with themes: {themes}")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "col_section": col_section,
                    "themes": themes,
                    "jurisdiction_type": state.jurisdiction.value if state.jurisdiction else "Civil-law jurisdiction"
                })
                logger.info(f"✅ COL issue identified: {result}")
                
            elif step_name == "analyze_courts_position":
                col_section = state.col_section[-1] if state.col_section else ""
                col_issue = state.col_issue[-1] if state.col_issue else ""
                themes = state.classification[-1].split(", ") if state.classification else []
                logger.info(f"🏛️ Analyzing court's position on: {col_issue}")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "col_section": col_section,
                    "col_issue": col_issue,
                    "themes": themes,
                    "jurisdiction_type": state.jurisdiction.value if state.jurisdiction else "Civil-law jurisdiction"
                })
                logger.info(f"✅ Court's position analyzed: {len(result)} characters")
                
            elif step_name in ["extract_obiter_dicta", "extract_dissenting_opinions"]:
                col_section = state.col_section[-1] if state.col_section else ""
                logger.info(f"⚖️ Extracting {step_name.replace('_', ' ')} for common law case...")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "col_section": col_section,
                    "jurisdiction_type": state.jurisdiction.value if state.jurisdiction else "Civil-law jurisdiction"
                })
                logger.info(f"✅ {step_name.replace('_', ' ').title()} extracted")
                
            elif step_name == "generate_abstract":
                logger.info(f"📄 Generating comprehensive abstract...")
                case_data = {
                    "jurisdiction": state.jurisdiction.value if state.jurisdiction else "Unknown",
                    "classification": state.classification,
                    "relevant_facts": state.relevant_facts[-1] if state.relevant_facts else "",
                    "pil_provisions": state.pil_provisions,
                    "col_issue": state.col_issue[-1] if state.col_issue else "",
                    "courts_position": state.courts_position[-1] if state.courts_position else ""
                }
                result = tool_func.invoke({"case_data": case_data})
                logger.info(f"✅ Abstract generated: {len(result)} characters")
                
            else:
                # Generic execution fallback
                logger.info(f"🔧 Generic execution for: {step_name}")
                result = tool_func.invoke({
                    "case_text": state.full_text,
                    "jurisdiction_type": state.jurisdiction.value if state.jurisdiction else "Civil-law jurisdiction"
                })
            
            execution_time = time.time() - start_time
            
            # Update execution logs with success
            execution_entry.update({
                "end_time": time.time(),
                "execution_time": execution_time,
                "status": "completed",
                "result_type": type(result).__name__,
                "result_length": len(str(result)) if result else 0
            })
            
            # Update both logs
            tool_execution_log[-1].update(execution_entry)
            session_activity_log[state.session_id][-1].update(execution_entry)
            
            logger.info(f"✅ Tool {step_name} completed in {execution_time:.2f}s")
            
            return {
                "tool_name": step_name,
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            # Update execution logs with error
            execution_entry.update({
                "end_time": time.time(),
                "execution_time": execution_time,
                "status": "error",
                "error": error_msg
            })
            
            # Update both logs
            tool_execution_log[-1].update(execution_entry)
            session_activity_log[state.session_id][-1].update(execution_entry)
            
            logger.error(f"❌ Tool {step_name} failed after {execution_time:.2f}s: {error_msg}")
            raise

# ========== INITIALIZE COMPONENTS ==========

# Initialize the language model
model = ChatOpenAI(model="gpt-4o-mini", streaming=True)

# Initialize orchestrator
orchestrator = LegalAnalysisOrchestrator(model)

# In-memory session storage (in production, use a proper database)
session_storage: Dict[str, AnalysisState] = {}

# Tool execution monitoring
tool_execution_log: List[Dict[str, Any]] = []
session_activity_log: Dict[str, List[Dict[str, Any]]] = {}

# Initialize FastAPI app
app = FastAPI(
    title="Legal Case Analyzer API - Professional Edition",
    version="2.0.0",
    description="Advanced legal case analysis with specialized PIL/COL tools"
)

# CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development: allow all; tighten for production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== API ENDPOINTS ==========

@app.get("/")
async def root():
    return {
        "message": "Legal Case Analyzer API - Professional Edition",
        "version": "2.0.0",
        "capabilities": [
            "Jurisdiction Detection",
            "Choice of Law Analysis", 
            "Theme Classification",
            "PIL Provision Extraction",
            "Streaming Analysis",
            "Multi-pattern Workflows"
        ]
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_case(request: LegalCaseRequest):
    """
    Comprehensive legal case analysis with customizable patterns and stages.
    """
    try:
        # Create or get analysis state
        state = session_storage.get(request.session_id)
        if not state:
            state = AnalysisState(
                session_id=request.session_id,
                case_citation=request.case_citation,
                full_text=request.full_text
            )
            session_storage[request.session_id] = state
        
        # Execute analysis based on pattern
        if request.pattern == AnalysisPattern.QUICK:
            # Quick analysis: jurisdiction + basic classification
            if not state.jurisdiction:
                result = await orchestrator.execute_step("detect_jurisdiction", state)
                jurisdiction_data = result["result"]
                state.jurisdiction = JurisdictionType(jurisdiction_data["jurisdiction_type"])
                state.precise_jurisdiction = jurisdiction_data["precise_jurisdiction"]
            
            if not state.classification:
                result = await orchestrator.execute_step("classify_themes", state)
                state.classification = [", ".join(result["result"])]
        
        elif request.pattern == AnalysisPattern.COMPREHENSIVE:
            # Full analysis pipeline
            pipeline = orchestrator.get_analysis_pipeline(state.jurisdiction or JurisdictionType.CIVIL_LAW)
            
            for step in pipeline:
                if step == "detect_jurisdiction" and not state.jurisdiction:
                    result = await orchestrator.execute_step(step, state)
                    jurisdiction_data = result["result"]
                    state.jurisdiction = JurisdictionType(jurisdiction_data["jurisdiction_type"])
                    state.precise_jurisdiction = jurisdiction_data["precise_jurisdiction"]
                    
                elif step == "extract_col_section" and not state.col_section:
                    result = await orchestrator.execute_step(step, state)
                    state.col_section.append(result["result"])
                    
                elif step == "classify_themes" and not state.classification:
                    result = await orchestrator.execute_step(step, state)
                    themes = result["result"]
                    state.classification.append(", ".join(themes) if isinstance(themes, list) else str(themes))
                    
                elif step == "analyze_relevant_facts" and not state.relevant_facts:
                    result = await orchestrator.execute_step(step, state)
                    state.relevant_facts.append(result["result"])
                    
                elif step == "identify_pil_provisions" and not state.pil_provisions:
                    result = await orchestrator.execute_step(step, state)
                    provisions = result["result"]
                    state.pil_provisions.append(", ".join(provisions) if isinstance(provisions, list) else str(provisions))
                    
                elif step == "identify_col_issue" and not state.col_issue:
                    result = await orchestrator.execute_step(step, state)
                    state.col_issue.append(result["result"])
                    
                elif step == "analyze_courts_position" and not state.courts_position:
                    result = await orchestrator.execute_step(step, state)
                    state.courts_position.append(result["result"])
                    
                elif step == "extract_obiter_dicta" and not state.obiter_dicta and state.jurisdiction == JurisdictionType.COMMON_LAW:
                    result = await orchestrator.execute_step(step, state)
                    state.obiter_dicta.append(result["result"])
                    
                elif step == "extract_dissenting_opinions" and not state.dissenting_opinions and state.jurisdiction == JurisdictionType.COMMON_LAW:
                    result = await orchestrator.execute_step(step, state)
                    state.dissenting_opinions.append(result["result"])
                    
                elif step == "generate_abstract" and not state.abstract:
                    result = await orchestrator.execute_step(step, state)
                    state.abstract.append(result["result"])
                    state.analysis_done = True
        
        # Calculate completion percentage
        total_steps = len(orchestrator.get_analysis_pipeline(state.jurisdiction or JurisdictionType.CIVIL_LAW))
        completed_steps = sum([
            1 if state.jurisdiction else 0,
            1 if state.col_section else 0,
            1 if state.classification else 0,
            1 if state.relevant_facts else 0,
            1 if state.pil_provisions else 0,
            1 if state.col_issue else 0,
            1 if state.courts_position else 0,
            1 if state.abstract else 0
        ])
        completion_percentage = (completed_steps / total_steps) * 100
        
        return AnalysisResponse(
            session_id=request.session_id,
            stage=state.analysis_stage,
            result={
                "jurisdiction": state.jurisdiction.value if state.jurisdiction else None,
                "precise_jurisdiction": state.precise_jurisdiction,
                "classification": state.classification,
                "col_section": state.col_section,
                "relevant_facts": state.relevant_facts,
                "pil_provisions": state.pil_provisions,
                "col_issue": state.col_issue,
                "courts_position": state.courts_position,
                "obiter_dicta": state.obiter_dicta,
                "dissenting_opinions": state.dissenting_opinions,
                "abstract": state.abstract
            },
            jurisdiction=state.jurisdiction,
            completion_percentage=completion_percentage,
            next_stage=None if completion_percentage >= 100 else AnalysisStage.COMPLETE
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/chat/stream")
async def stream_legal_chat(request: StreamChatRequest):
    """
    Streaming legal analysis chat with contextual awareness.
    """
    async def generate_stream():
        try:
            # Get analysis context if available
            state = session_storage.get(request.session_id)
            context_info = ""
            
            if state and state.jurisdiction:
                context_info = f"\nContext: This is a {state.jurisdiction.value} case"
                if state.case_citation:
                    context_info += f" ({state.case_citation})"
                if state.classification:
                    context_info += f"\nThemes: {state.classification[-1]}"
                if state.col_issue:
                    context_info += f"\nCOL Issue: {state.col_issue[-1]}"
            
            # Enhanced system prompt for legal analysis
            system_prompt = SystemMessage(
                "You are an expert legal assistant specializing in private international law, "
                "choice of law, and conflict of laws. You can analyze court decisions, extract "
                "legal principles, and provide insights on PIL issues. Always provide thorough "
                "and professional responses while noting that your advice should not replace "
                "consultation with qualified legal professionals." + context_info
            )
            
            user_message = HumanMessage(content=request.message)
            messages = [system_prompt, user_message]
            
            accumulated_content = ""
            
            async for chunk in model.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    accumulated_content += chunk.content
                    yield f"data: {json.dumps({'content': chunk.content, 'session_id': request.session_id, 'done': False, 'type': 'token'})}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'content': '', 'session_id': request.session_id, 'done': True, 'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Error: {str(e)}', 'session_id': request.session_id, 'done': True, 'type': 'error'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.get("/tools")
async def list_legal_tools():
    """List available legal analysis tools and patterns."""
    return {
        "tools": [
            {"id": "detect_jurisdiction", "description": "Detect legal system type and jurisdiction"},
            {"id": "extract_col_section", "description": "Extract choice of law sections"},
            {"id": "classify_themes", "description": "Classify PIL themes"},
            {"id": "analyze_relevant_facts", "description": "Extract relevant facts for COL analysis"},
            {"id": "identify_pil_provisions", "description": "Identify PIL provisions cited"},
            {"id": "identify_col_issue", "description": "Identify main choice of law issue"},
            {"id": "analyze_courts_position", "description": "Analyze court's position on COL issue"},
            {"id": "extract_obiter_dicta", "description": "Extract obiter dicta (common law)"},
            {"id": "extract_dissenting_opinions", "description": "Extract dissenting opinions (common law)"},
            {"id": "generate_abstract", "description": "Generate comprehensive case abstract"}
        ],
        "patterns": [
            {"id": "quick", "description": "Basic jurisdiction detection and theme classification"},
            {"id": "sequential", "description": "Step-by-step analysis workflow"},
            {"id": "parallel", "description": "Multiple analysis perspectives simultaneously"},
            {"id": "comprehensive", "description": "Complete PIL/COL analysis pipeline"}
        ],
        "jurisdictions": [
            {"id": "civil_law", "description": "Civil law jurisdiction analysis"},
            {"id": "common_law", "description": "Common law jurisdiction analysis (includes obiter dicta, dissenting opinions)"},
            {"id": "mixed", "description": "Mixed jurisdiction analysis"}
        ]
    }

@app.get("/sessions")
async def list_sessions():
    """List all active analysis sessions."""
    return {
        "sessions": [
            {
                "session_id": session_id,
                "case_citation": state.case_citation,
                "jurisdiction": state.jurisdiction.value if state.jurisdiction else None,
                "analysis_stage": state.analysis_stage.value,
                "completion": f"{len([x for x in [state.jurisdiction, state.col_section, state.classification, state.relevant_facts, state.pil_provisions, state.col_issue, state.courts_position, state.abstract] if x])/8*100:.0f}%"
            }
            for session_id, state in session_storage.items()
        ],
        "count": len(session_storage)
    }

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific analysis session."""
    if session_id in session_storage:
        del session_storage[session_id]
        return {"message": f"Session {session_id} cleared"}
    else:
        return {"message": f"Session {session_id} not found"}

@app.get("/sessions/{session_id}/export")
async def export_session(session_id: str):
    """Export complete analysis results for a session."""
    state = session_storage.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "case_citation": state.case_citation,
        "jurisdiction": state.jurisdiction.value if state.jurisdiction else None,
        "precise_jurisdiction": state.precise_jurisdiction,
        "analysis_results": {
            "col_section": state.col_section,
            "themes": state.classification,
            "relevant_facts": state.relevant_facts,
            "pil_provisions": state.pil_provisions,
            "col_issue": state.col_issue,
            "courts_position": state.courts_position,
            "obiter_dicta": state.obiter_dicta,
            "dissenting_opinions": state.dissenting_opinions,
            "abstract": state.abstract
        },
        "chat_history": state.chat_history,
        "analysis_complete": state.analysis_done
    }

# Monitoring endpoints
@app.get("/api/monitoring/tool-calls", response_model=Dict[str, Any])
async def get_tool_execution_log(limit: int = 50, session_id: Optional[str] = None):
    """
    Get tool execution logs for monitoring and debugging
    
    Args:
        limit: Maximum number of entries to return (default: 50)
        session_id: Optional session ID to filter logs
    
    Returns:
        Dict containing tool execution logs and statistics
    """
    filtered_logs = tool_execution_log
    
    if session_id:
        filtered_logs = [log for log in tool_execution_log if log.get("session_id") == session_id]
    
    # Get recent logs within limit
    recent_logs = filtered_logs[-limit:] if limit > 0 else filtered_logs
    
    # Calculate statistics
    total_executions = len(filtered_logs)
    successful_executions = len([log for log in filtered_logs if log.get("status") == "completed"])
    failed_executions = len([log for log in filtered_logs if log.get("status") == "error"])
    avg_execution_time = sum(log.get("execution_time", 0) for log in filtered_logs if log.get("execution_time")) / max(1, len([log for log in filtered_logs if log.get("execution_time")]))
    
    # Tool usage statistics
    tool_usage = {}
    for log in filtered_logs:
        tool_name = log.get("tool_name", "unknown")
        if tool_name not in tool_usage:
            tool_usage[tool_name] = {"count": 0, "success": 0, "failures": 0, "total_time": 0}
        tool_usage[tool_name]["count"] += 1
        if log.get("status") == "completed":
            tool_usage[tool_name]["success"] += 1
        elif log.get("status") == "error":
            tool_usage[tool_name]["failures"] += 1
        if log.get("execution_time"):
            tool_usage[tool_name]["total_time"] += log.get("execution_time", 0)
    
    return {
        "statistics": {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": (successful_executions / max(1, total_executions)) * 100,
            "average_execution_time": round(avg_execution_time, 3),
            "active_sessions": len(session_activity_log),
            "tool_usage": tool_usage
        },
        "recent_logs": recent_logs,
        "filter_applied": {
            "session_id": session_id,
            "limit": limit
        }
    }

@app.get("/api/monitoring/session/{session_id}", response_model=Dict[str, Any])
async def get_session_activity(session_id: str):
    """
    Get detailed activity log for a specific session
    
    Args:
        session_id: The session ID to get activity for
    
    Returns:
        Dict containing session activity and analysis
    """
    if session_id not in session_activity_log:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    session_logs = session_activity_log[session_id]
    
    # Calculate session statistics
    total_tools = len(session_logs)
    successful_tools = len([log for log in session_logs if log.get("status") == "completed"])
    failed_tools = len([log for log in session_logs if log.get("status") == "error"])
    total_time = sum(log.get("execution_time", 0) for log in session_logs if log.get("execution_time"))
    
    # Get session state if exists
    session_state = None
    if session_id in sessions:
        state = sessions[session_id]
        session_state = {
            "case_citation": state.case_citation,
            "jurisdiction": state.jurisdiction.value if state.jurisdiction else None,
            "analysis_progress": {
                "col_section": len(state.col_section),
                "classification": len(state.classification),
                "relevant_facts": len(state.relevant_facts),
                "pil_provisions": len(state.pil_provisions),
                "col_issue": len(state.col_issue),
                "courts_position": len(state.courts_position),
                "analysis_complete": state.analysis_complete
            }
        }
    
    return {
        "session_id": session_id,
        "session_state": session_state,
        "activity_summary": {
            "total_tool_calls": total_tools,
            "successful_calls": successful_tools,
            "failed_calls": failed_tools,
            "success_rate": (successful_tools / max(1, total_tools)) * 100,
            "total_execution_time": round(total_time, 3),
            "average_execution_time": round(total_time / max(1, total_tools), 3)
        },
        "detailed_logs": session_logs
    }

@app.get("/api/monitoring/live-status", response_model=Dict[str, Any])
async def get_live_status():
    """
    Get live system status and current activity
    
    Returns:
        Dict containing current system status and active operations
    """
    current_time = time.time()
    
    # Find currently running operations (started but not completed in last 5 minutes)
    active_operations = []
    for log in tool_execution_log:
        if (log.get("status") == "started" and 
            current_time - log.get("start_time", 0) < 300):  # 5 minutes
            active_operations.append({
                "session_id": log.get("session_id"),
                "tool_name": log.get("tool_name"),
                "started_at": log.get("start_time"),
                "running_for": round(current_time - log.get("start_time", 0), 2)
            })
    
    # Recent activity (last 10 minutes)
    recent_cutoff = current_time - 600  # 10 minutes
    recent_activity = [
        log for log in tool_execution_log 
        if log.get("start_time", 0) > recent_cutoff
    ]
    
    return {
        "timestamp": current_time,
        "system_status": {
            "active_sessions": len(sessions),
            "total_tool_executions": len(tool_execution_log),
            "currently_running": len(active_operations),
            "recent_activity_count": len(recent_activity)
        },
        "active_operations": active_operations,
        "recent_activity": recent_activity[-20:],  # Last 20 recent activities
        "available_tools": list(LegalAnalysisOrchestrator().tools.keys())
    }

@app.websocket("/api/monitoring/live-feed")
async def monitoring_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time monitoring of tool executions
    """
    await websocket.accept()
    last_log_count = len(tool_execution_log)
    
    try:
        while True:
            current_log_count = len(tool_execution_log)
            
            # Check for new log entries
            if current_log_count > last_log_count:
                new_logs = tool_execution_log[last_log_count:]
                for log in new_logs:
                    await websocket.send_json({
                        "type": "tool_execution",
                        "data": log,
                        "timestamp": time.time()
                    })
                last_log_count = current_log_count
            
            # Send periodic status updates
            await websocket.send_json({
                "type": "status_update",
                "data": {
                    "active_sessions": len(sessions),
                    "total_executions": len(tool_execution_log),
                    "timestamp": time.time()
                }
            })
            
            await asyncio.sleep(1)  # Update every second
            
    except WebSocketDisconnect:
        logger.info("Monitoring WebSocket disconnected")
    except Exception as e:
        logger.error(f"Monitoring WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    print("Starting Legal Case Analyzer API - Professional Edition...")
    print("Enhanced with PIL/COL analysis tools")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
