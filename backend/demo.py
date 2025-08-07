"""
Demo script for Legal Case Analyzer API

This script demonstrates the key features of the LangGraph-powered legal assistant.
Run this after starting the API server to see it in action.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any


class LegalAnalyzerDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"demo_session_{int(time.time())}"
        
    async def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the legal analyzer API"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat",
                json={"message": message, "session_id": self.session_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}: {await response.text()}"}
    
    async def get_history(self) -> Dict[str, Any]:
        """Get conversation history"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/chat/history/{self.session_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}: {await response.text()}"}
    
    async def check_health(self) -> bool:
        """Check if the API server is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    def print_separator(self, title: str = ""):
        """Print a nice separator"""
        print("=" * 60)
        if title:
            print(f" {title} ".center(60))
            print("=" * 60)
        print()
    
    def print_message(self, role: str, content: str):
        """Print a formatted message"""
        emoji = "👤" if role == "user" else "🤖"
        print(f"{emoji} {role.title()}: {content}")
        print()
    
    async def run_demo(self):
        """Run the complete demonstration"""
        
        self.print_separator("Legal Case Analyzer API Demo")
        
        # Check if server is running
        print("🔍 Checking if API server is running...")
        if not await self.check_health():
            print("❌ API server is not running!")
            print("Please start the server first:")
            print("   python run_dev.py")
            return
        
        print("✅ API server is running!")
        print(f"📱 Using session ID: {self.session_id}")
        print()
        
        # Demo scenarios
        scenarios = [
            {
                "title": "Contract Dispute Analysis",
                "message": "I have a contract dispute case where the defendant claims breach of contract due to delayed delivery. The original contract specified delivery within 30 days, but delivery took 45 days due to supply chain issues. Can you help me analyze this case?"
            },
            {
                "title": "Legal Precedent Search",
                "message": "What legal precedents should I look for regarding force majeure clauses in commercial contracts during supply chain disruptions?"
            },
            {
                "title": "Employment Law Question",
                "message": "An employee was terminated for poor performance, but they claim it was discriminatory. They were the only person of their demographic in the department. How should I approach this case?"
            },
            {
                "title": "Tool Usage Example",
                "message": "Please analyze the following case details: A software company is suing a former employee for breach of non-compete agreement. The employee started a competing business within 6 months of leaving."
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            self.print_separator(f"Demo Scenario {i}: {scenario['title']}")
            
            # Send message
            self.print_message("user", scenario["message"])
            
            print("🔄 Sending message to AI assistant...")
            response = await self.send_message(scenario["message"])
            
            if "error" in response:
                print(f"❌ Error: {response['error']}")
                continue
            
            self.print_message("assistant", response.get("response", "No response"))
            
            # Wait a bit between scenarios
            if i < len(scenarios):
                print("⏱️  Waiting 2 seconds before next scenario...")
                await asyncio.sleep(2)
        
        # Show conversation history
        self.print_separator("Conversation History")
        
        print("📜 Retrieving conversation history...")
        history = await self.get_history()
        
        if "error" not in history:
            print(f"💬 Found {len(history.get('messages', []))} messages in history")
            print()
            
            for i, msg in enumerate(history.get('messages', []), 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                print(f"{i}. {role.title()}: {content[:100]}{'...' if len(content) > 100 else ''}")
        else:
            print(f"❌ Error getting history: {history['error']}")
        
        self.print_separator("Demo Complete")
        print("✅ Demo completed successfully!")
        print(f"🌐 Visit http://localhost:8000/docs to explore the API interactively")
        print(f"📝 Session ID was: {self.session_id}")


async def main():
    """Main demo function"""
    demo = LegalAnalyzerDemo()
    
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Make sure the API server is running: python run_dev.py")


if __name__ == "__main__":
    asyncio.run(main())
