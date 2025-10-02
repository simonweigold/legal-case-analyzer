#!/usr/bin/env python3
"""
Test script for the enhanced legal analysis tools
"""

import os
import sys

# Add the backend directory to the path
sys.path.insert(0, '/Users/simonweigold/dev/legal-case-analyzer/backend')

def test_basic_functionality():
    """Test basic tool functionality without LLM calls"""
    try:
        from tools.tools import (
            load_jurisdictions, 
            load_themes, 
            get_jurisdiction_legal_system_mapping,
            get_tools,
            get_tools_by_name
        )
        
        print("Testing data loading...")
        
        # Test jurisdiction loading
        jurisdictions = load_jurisdictions()
        print(f"Loaded {len(jurisdictions)} jurisdictions")
        if jurisdictions:
            print(f"Sample jurisdiction: {jurisdictions[0]['name']}")
        
        # Test themes loading
        themes = load_themes()
        print(f"Loaded {len(themes)} themes")
        if themes:
            print(f"Sample theme: {themes[0]['theme']}")
        
        # Test legal system mapping
        mapping = get_jurisdiction_legal_system_mapping()
        print(f"Legal system mapping contains {len(mapping)} entries")
        
        # Test tool registry
        tools = get_tools()
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description.split('.')[0]}")
        
        tools_by_name = get_tools_by_name()
        print(f"Tools by name contains {len(tools_by_name)} entries")
        
        print("\n✅ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
        return False

if __name__ == "__main__":
    print("Legal Case Analyzer - Tools Test")
    print("=" * 40)
    
    success = test_basic_functionality()
    
    if success:
        print("\n🎉 Tool implementation successful!")
        print("\nNew tools available:")
        print("- detect_legal_system_type: Detects Civil-law vs Common-law jurisdiction")
        print("- detect_precise_jurisdiction: Identifies specific jurisdiction from text")
        print("- extract_choice_of_law_section: Extracts COL analysis from decisions")
        print("- classify_legal_themes: Classifies themes like Party autonomy, etc.")
        print("- identify_choice_of_law_issue: Identifies specific COL issues")
        print("- analyze_courts_position: Analyzes court's reasoning and position")
        print("- analyze_legal_case: Comprehensive analysis using all tools")
    else:
        print("\n❌ Tool implementation has issues that need to be resolved.")
        sys.exit(1)
