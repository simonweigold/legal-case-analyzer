#!/usr/bin/env python3
"""
Test script for monitoring the enhanced legal case analyzer API
Demonstrates how to check tool calls and system activity
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, Any

class LegalAPIMonitor:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def test_basic_analysis_with_monitoring(self):
        """Run a basic analysis and monitor tool calls"""
        print("🔬 Testing Legal Analysis with Tool Monitoring")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # Start a new analysis session
            print("\n1. Starting new analysis session...")
            session_response = await self._post_json(session, "/api/analyze/start", {
                "case_text": """
                In the case of Smith v. International Corp., decided by the High Court of Justice in London,
                the court addressed a complex choice of law issue involving a contract dispute between
                parties from different jurisdictions. The contract was formed in New York but was to be
                performed in Germany, with the plaintiff domiciled in England and the defendant
                incorporated in Delaware.
                
                The court applied English conflict of laws rules to determine that German law should
                govern the substantive issues of the contract, while English procedural law applied
                to the litigation process.
                """,
                "case_citation": "Smith v. International Corp. [2023] EWHC 1234 (Comm)"
            })
            
            session_id = session_response.get("session_id")
            print(f"✅ Session created: {session_id}")
            
            # Monitor initial status
            await self._check_monitoring_status()
            
            # Execute analysis steps with monitoring
            print("\n2. Running jurisdiction detection...")
            await self._post_json(session, f"/api/analyze/{session_id}/jurisdiction")
            await self._show_recent_tool_calls(session)
            
            print("\n3. Extracting COL section...")
            await self._post_json(session, f"/api/analyze/{session_id}/col-section")
            await self._show_recent_tool_calls(session)
            
            print("\n4. Classifying themes...")
            await self._post_json(session, f"/api/analyze/{session_id}/themes")
            await self._show_recent_tool_calls(session)
            
            print("\n5. Final session analysis...")
            await self._show_session_details(session, session_id)
            
            print("\n6. System-wide monitoring stats...")
            await self._show_system_stats(session)

    async def _post_json(self, session: aiohttp.ClientSession, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make a POST request and return JSON response"""
        url = f"{self.base_url}{endpoint}"
        async with session.post(url, json=data or {}) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                print(f"❌ Error {response.status}: {error_text}")
                return {}

    async def _get_json(self, session: aiohttp.ClientSession, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make a GET request and return JSON response"""
        url = f"{self.base_url}{endpoint}"
        async with session.get(url, params=params or {}) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                print(f"❌ Error {response.status}: {error_text}")
                return {}

    async def _check_monitoring_status(self):
        """Check overall monitoring status"""
        async with aiohttp.ClientSession() as session:
            status = await self._get_json(session, "/api/monitoring/live-status")
            
            if status:
                system_status = status.get("system_status", {})
                print(f"📊 System Status:")
                print(f"   Active Sessions: {system_status.get('active_sessions', 0)}")
                print(f"   Total Tool Executions: {system_status.get('total_tool_executions', 0)}")
                print(f"   Currently Running: {system_status.get('currently_running', 0)}")

    async def _show_recent_tool_calls(self, session: aiohttp.ClientSession, limit: int = 3):
        """Show recent tool calls"""
        tool_logs = await self._get_json(session, "/api/monitoring/tool-calls", {"limit": limit})
        
        if tool_logs and "recent_logs" in tool_logs:
            print(f"🔧 Recent Tool Calls:")
            for log in tool_logs["recent_logs"][-limit:]:
                status_emoji = "✅" if log.get("status") == "completed" else "⏳" if log.get("status") == "started" else "❌"
                tool_name = log.get("tool_name", "unknown")
                exec_time = log.get("execution_time", 0)
                print(f"   {status_emoji} {tool_name} ({exec_time:.2f}s)")

    async def _show_session_details(self, session: aiohttp.ClientSession, session_id: str):
        """Show detailed session activity"""
        session_details = await self._get_json(session, f"/api/monitoring/session/{session_id}")
        
        if session_details:
            summary = session_details.get("activity_summary", {})
            print(f"📋 Session {session_id} Analysis:")
            print(f"   Total Tool Calls: {summary.get('total_tool_calls', 0)}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
            print(f"   Total Execution Time: {summary.get('total_execution_time', 0):.2f}s")
            print(f"   Average per Tool: {summary.get('average_execution_time', 0):.2f}s")

    async def _show_system_stats(self, session: aiohttp.ClientSession):
        """Show system-wide statistics"""
        tool_logs = await self._get_json(session, "/api/monitoring/tool-calls", {"limit": 100})
        
        if tool_logs and "statistics" in tool_logs:
            stats = tool_logs["statistics"]
            print(f"📈 System Statistics:")
            print(f"   Total Executions: {stats.get('total_executions', 0)}")
            print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
            print(f"   Average Execution Time: {stats.get('average_execution_time', 0):.3f}s")
            print(f"   Active Sessions: {stats.get('active_sessions', 0)}")
            
            # Show tool usage breakdown
            tool_usage = stats.get("tool_usage", {})
            if tool_usage:
                print(f"\n🔧 Tool Usage Breakdown:")
                for tool_name, usage in tool_usage.items():
                    success_rate = (usage["success"] / max(1, usage["count"])) * 100
                    avg_time = usage["total_time"] / max(1, usage["count"])
                    print(f"   {tool_name}: {usage['count']} calls, {success_rate:.1f}% success, {avg_time:.2f}s avg")

    async def test_websocket_monitoring(self):
        """Test real-time monitoring via WebSocket"""
        print("\n🔌 Testing Real-time WebSocket Monitoring")
        print("=" * 60)
        
        import websockets
        uri = f"ws://localhost:8000/api/monitoring/live-feed"
        
        try:
            async with websockets.connect(uri) as websocket:
                print("✅ Connected to monitoring WebSocket")
                
                # Listen for a few messages
                for i in range(5):
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(message)
                        msg_type = data.get("type")
                        
                        if msg_type == "tool_execution":
                            tool_data = data.get("data", {})
                            print(f"🔧 Tool Execution: {tool_data.get('tool_name')} ({tool_data.get('status')})")
                        elif msg_type == "status_update":
                            status_data = data.get("data", {})
                            print(f"📊 Status: {status_data.get('active_sessions')} sessions, {status_data.get('total_executions')} executions")
                        
                    except asyncio.TimeoutError:
                        print("⏱️ No new messages (timeout)")
                        break
                        
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            print("💡 Make sure the API server is running and WebSocket endpoint is available")

async def main():
    """Run all monitoring tests"""
    monitor = LegalAPIMonitor()
    
    print("🚀 Legal API Monitoring Test Suite")
    print("=" * 80)
    
    try:
        # Test 1: Basic analysis with monitoring
        await monitor.test_basic_analysis_with_monitoring()
        
        # Small delay before WebSocket test
        await asyncio.sleep(1)
        
        # Test 2: WebSocket monitoring (requires websockets package)
        try:
            import websockets
            await monitor.test_websocket_monitoring()
        except ImportError:
            print("\n💡 WebSocket test skipped (install 'websockets' package to enable)")
            print("   pip install websockets")
        
        print("\n✅ All monitoring tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("💡 Make sure the enhanced API server is running: python main_enhanced.py")

if __name__ == "__main__":
    asyncio.run(main())
