#!/usr/bin/env python3
"""
Test script for the enhanced Legal Case Analyzer API.
"""

import asyncio
import aiohttp
import json


async def test_enhanced_api():
    """Test the enhanced legal analysis API."""
    
    # Sample legal case text
    sample_case = {
        "case_citation": "BGH, Urteil vom 15.12.2020 - XI ZR 234/19",
        "full_text": """
        The Federal Court of Justice of Germany addressed a choice of law issue in this cross-border contract dispute.
        The parties, a German company and a Swiss corporation, entered into a distribution agreement.
        The contract contained a choice of law clause selecting Swiss law to govern the agreement.
        The court had to determine whether this choice was valid and effective under German private international law.
        The relevant provisions include Article 187 of the Swiss Private International Law Act and 
        the Rome I Regulation provisions on contractual obligations.
        The court held that parties to a commercial contract have broad autonomy to choose the applicable law,
        even where there is no significant connection to the chosen jurisdiction.
        This decision confirms the principle of party autonomy in choice of law matters.
        """,
        "session_id": "test-enhanced-001",
        "pattern": "comprehensive"
    }
    
    url = "http://localhost:8000/analyze"
    
    print("Testing Enhanced Legal Case Analyzer API")
    print("=" * 50)
    print(f"Case Citation: {sample_case['case_citation']}")
    print(f"Pattern: {sample_case['pattern']}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=sample_case) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    print("Analysis Results:")
                    print(f"Session ID: {result['session_id']}")
                    print(f"Stage: {result['stage']}")
                    print(f"Jurisdiction: {result.get('jurisdiction')}")
                    print(f"Completion: {result['completion_percentage']:.1f}%")
                    print()
                    
                    # Display analysis results
                    analysis_result = result['result']
                    
                    if analysis_result.get('jurisdiction'):
                        print(f"🏛️  Jurisdiction Type: {analysis_result['jurisdiction']}")
                        
                    if analysis_result.get('precise_jurisdiction'):
                        print(f"📍 Precise Jurisdiction: {analysis_result['precise_jurisdiction']}")
                        
                    if analysis_result.get('classification'):
                        print(f"🏷️  Themes: {analysis_result['classification']}")
                        
                    if analysis_result.get('col_section'):
                        print(f"⚖️  COL Section: {analysis_result['col_section'][0][:100]}...")
                        
                    if analysis_result.get('relevant_facts'):
                        print(f"📋 Relevant Facts: {analysis_result['relevant_facts'][0][:100]}...")
                        
                    if analysis_result.get('pil_provisions'):
                        print(f"📖 PIL Provisions: {analysis_result['pil_provisions']}")
                        
                    if analysis_result.get('col_issue'):
                        print(f"❓ COL Issue: {analysis_result['col_issue'][0]}")
                        
                    if analysis_result.get('courts_position'):
                        print(f"🏛️  Court's Position: {analysis_result['courts_position'][0][:100]}...")
                        
                    if analysis_result.get('abstract'):
                        print(f"📄 Abstract: {analysis_result['abstract'][0][:150]}...")
                
                else:
                    error_text = await response.text()
                    print(f"❌ Error: HTTP {response.status}")
                    print(f"Response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        print("Make sure the enhanced API server is running on http://localhost:8000")


async def test_tools_endpoint():
    """Test the tools endpoint."""
    print("\n" + "=" * 50)
    print("Testing Tools Endpoint")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/tools") as response:
                if response.status == 200:
                    tools_data = await response.json()
                    
                    print("Available Tools:")
                    for tool in tools_data['tools']:
                        print(f"  • {tool['id']}: {tool['description']}")
                    
                    print("\nAnalysis Patterns:")
                    for pattern in tools_data['patterns']:
                        print(f"  • {pattern['id']}: {pattern['description']}")
                    
                    print("\nSupported Jurisdictions:")
                    for jurisdiction in tools_data['jurisdictions']:
                        print(f"  • {jurisdiction['id']}: {jurisdiction['description']}")
                        
                else:
                    print(f"❌ Error accessing tools: HTTP {response.status}")
                    
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def test_streaming_chat():
    """Test the enhanced streaming chat."""
    print("\n" + "=" * 50)
    print("Testing Enhanced Streaming Chat")
    print("-" * 50)
    
    url = "http://localhost:8000/chat/stream"
    
    payload = {
        "message": "What are the key principles of party autonomy in choice of law under German private international law?",
        "session_id": "test-enhanced-001",  # Use same session as analysis
        "context": {"analysis_available": True}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    print(f"Question: {payload['message']}")
    print("-" * 50)
    print("Response:")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                if data.get('content'):
                                    print(data['content'], end='', flush=True)
                                elif data.get('done'):
                                    print("\n" + "-" * 50)
                                    print("✅ Streaming completed")
                                    break
                                elif data.get('error'):
                                    print(f"\n❌ Error: {data['error']}")
                                    break
                            except json.JSONDecodeError:
                                pass
                else:
                    print(f"❌ Error: HTTP {response.status}")
                    
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("Enhanced Legal Case Analyzer - API Test Suite")
    print("Make sure the enhanced API server is running on http://localhost:8000")
    print()
    
    asyncio.run(test_enhanced_api())
    asyncio.run(test_tools_endpoint())
    asyncio.run(test_streaming_chat())
