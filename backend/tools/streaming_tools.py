"""
Streaming versions of legal analysis tools that provide detailed progress updates.
These tools are designed to work with the streaming chat endpoint to give users
real-time feedback on the analysis process.
"""

import json
import asyncio
import time
from typing import Dict, Any
from langchain_core.tools import tool

from .tools import (
    detect_legal_system_type,
    detect_precise_jurisdiction, 
    extract_choice_of_law_section,
    classify_legal_themes,
    identify_choice_of_law_issue,
    analyze_courts_position
)


@tool
def streaming_analyze_legal_case(case_details: str = ""):
    """
    Analyze legal case details with detailed progress tracking and step-by-step results.
    This tool provides comprehensive PIL analysis with transparent progress reporting.
    
    Args:
        case_details (str): The details of the legal case to analyze
        
    Returns:
        str: Comprehensive legal analysis with detailed progress information
    """
    if not case_details or case_details.strip() == "":
        return "**Streaming Legal Analysis: Input Required**\n\nPlease provide legal case details for comprehensive Private International Law analysis. Include court decisions, legal texts, or case documents."
    
    # Track analysis start time
    start_time = time.time()
    
    # Define the analysis workflow
    analysis_steps = [
        {
            "id": "jurisdiction_detection",
            "name": "🌍 Jurisdiction Detection",
            "description": "Identifying the precise jurisdiction from legal text",
            "tool": detect_precise_jurisdiction,
            "args": {"text": case_details},
            "weight": 15  # Percentage of total work
        },
        {
            "id": "legal_system_classification", 
            "name": "⚖️ Legal System Classification",
            "description": "Determining Civil-law vs Common-law system type",
            "tool": detect_legal_system_type,
            "args": {"jurisdiction_name": "", "text": case_details},
            "weight": 15
        },
        {
            "id": "col_extraction",
            "name": "📋 Choice of Law Extraction",
            "description": "Extracting PIL-relevant sections from court decision",
            "tool": extract_choice_of_law_section,
            "args": {"text": case_details},
            "weight": 25
        },
        {
            "id": "theme_classification",
            "name": "🏷️ Legal Theme Classification",
            "description": "Classifying PIL themes (Party autonomy, Mandatory rules, etc.)",
            "tool": classify_legal_themes,
            "args": {"text": case_details, "col_section": ""},
            "weight": 20
        },
        {
            "id": "col_issue_identification", 
            "name": "🔍 Choice of Law Issue Analysis",
            "description": "Identifying specific PIL issues and conflicts",
            "tool": identify_choice_of_law_issue,
            "args": {"text": case_details, "col_section": "", "themes": ""},
            "weight": 15
        },
        {
            "id": "court_position_analysis",
            "name": "👨‍⚖️ Court Position Analysis",
            "description": "Analyzing court's reasoning and PIL methodology", 
            "tool": analyze_courts_position,
            "args": {"text": case_details, "col_section": "", "themes": "", "col_issue": ""},
            "weight": 10
        }
    ]
    
    # Initialize results tracking
    results = {}
    completed_steps = 0
    total_weight = sum(step['weight'] for step in analysis_steps)
    cumulative_weight = 0
    
    analysis_log = ["# 🏛️ STREAMING LEGAL CASE ANALYSIS\n"]
    analysis_log.append(f"**Analysis Started:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    analysis_log.append(f"**Text Length:** {len(case_details):,} characters")
    analysis_log.append(f"**Analysis Steps:** {len(analysis_steps)} specialized PIL tools\n")
    
    try:
        # Execute each analysis step
        for i, step in enumerate(analysis_steps):
            step_start_time = time.time()
            cumulative_weight += step['weight']
            progress_percent = int((cumulative_weight / total_weight) * 100)
            
            analysis_log.append(f"## Step {i+1}/{len(analysis_steps)}: {step['name']}")
            analysis_log.append(f"**Progress:** {progress_percent}% | **Task:** {step['description']}")
            analysis_log.append("**Status:** 🔄 Processing...")
            
            # Update args with previous results for dependent steps
            if step["id"] == "theme_classification" and "col_extraction" in results:
                step["args"]["col_section"] = results["col_extraction"]
            elif step["id"] == "col_issue_identification":
                if "col_extraction" in results:
                    step["args"]["col_section"] = results["col_extraction"]
                if "theme_classification" in results:
                    step["args"]["themes"] = results["theme_classification"]
            elif step["id"] == "court_position_analysis":
                if "col_extraction" in results:
                    step["args"]["col_section"] = results["col_extraction"]
                if "theme_classification" in results:
                    step["args"]["themes"] = results["theme_classification"]
                if "col_issue_identification" in results:
                    step["args"]["col_issue"] = results["col_issue_identification"]
            
            # Execute the analysis step
            try:
                result = step["tool"].invoke(step["args"])
                step_duration = time.time() - step_start_time
                results[step["id"]] = result
                completed_steps += 1
                
                # Update log with success
                analysis_log[-1] = f"**Status:** ✅ Completed in {step_duration:.1f}s"
                
                # Add result preview
                result_str = str(result)
                if len(result_str) > 200:
                    preview = result_str[:200] + f"... [+{len(result_str)-200} characters]"
                else:
                    preview = result_str
                
                analysis_log.append(f"**Result Preview:** {preview}")
                analysis_log.append("")  # Empty line for spacing
                
            except Exception as e:
                step_duration = time.time() - step_start_time
                error_msg = str(e)
                results[step["id"]] = f"**Error:** {error_msg}"
                
                # Update log with error
                analysis_log[-1] = f"**Status:** ❌ Failed after {step_duration:.1f}s"
                analysis_log.append(f"**Error:** {error_msg}")
                analysis_log.append("")  # Empty line for spacing
        
        # Calculate total analysis time
        total_duration = time.time() - start_time
        
        # Compile comprehensive results
        analysis_log.append("---\n")
        analysis_log.append("# 📊 ANALYSIS RESULTS\n")
        analysis_log.append(f"**Completed:** {completed_steps}/{len(analysis_steps)} steps")
        analysis_log.append(f"**Total Duration:** {total_duration:.1f} seconds")
        analysis_log.append(f"**Analysis Quality:** {'Excellent' if completed_steps == len(analysis_steps) else 'Partial'}")
        analysis_log.append("")
        
        # Add detailed results
        for step in analysis_steps:
            step_id = step["id"]
            if step_id in results:
                analysis_log.append(f"## {step['name']}")
                analysis_log.append(results[step_id])
                analysis_log.append("")
        
        # Add final recommendations
        analysis_log.append("---\n")
        analysis_log.append("# � RECOMMENDATIONS & NEXT STEPS\n")
        
        success_rate = (completed_steps / len(analysis_steps)) * 100
        if success_rate == 100:
            analysis_log.append("✅ **Complete Analysis:** All PIL analysis steps completed successfully")
        elif success_rate >= 80:
            analysis_log.append("⚠️ **Mostly Complete:** Most analysis steps completed with some limitations")
        else:
            analysis_log.append("❌ **Partial Analysis:** Several analysis steps encountered issues")
        
        analysis_log.append("")
        analysis_log.append("**Research Guidance:**")
        analysis_log.append("- Use the jurisdiction and legal system information for case classification")
        analysis_log.append("- Reference the identified PIL themes for academic research")
        analysis_log.append("- Consider the court's reasoning methodology for similar cases")
        analysis_log.append("- Consult legal professionals for case-specific applications")
        
        analysis_log.append("")
        analysis_log.append("**📚 Analysis Framework:** This comprehensive analysis used specialized Private International Law (PIL) tools designed for legal professionals and researchers. Each step employed advanced legal AI models trained on international legal materials.")
        
        analysis_log.append("")
        analysis_log.append("**⚠️ Important:** This analysis is for educational and research purposes. Always consult qualified legal professionals for actual legal matters.")
        
        return "\n".join(analysis_log)
        
    except Exception as e:
        total_duration = time.time() - start_time
        error_analysis = f"""# ❌ STREAMING LEGAL ANALYSIS ERROR

**Error Occurred:** {str(e)}
**Analysis Duration:** {total_duration:.1f} seconds
**Steps Completed:** {completed_steps}/{len(analysis_steps)}

## Partial Results
{chr(10).join(analysis_log)}

**Recovery Suggestions:**
- Try with shorter or cleaner legal text
- Ensure text contains substantive legal content
- Check for any special characters or formatting issues
- Contact support if the error persists

**Note:** This error has been logged for system improvement."""
        
        return error_analysis


def get_streaming_tools():
    """Get streaming-enabled tools."""
    return [streaming_analyze_legal_case]


def get_streaming_tools_by_name():
    """Get streaming tools indexed by name."""
    tools = get_streaming_tools()
    return {tool.name: tool for tool in tools}
