"""
Test client for the Legal Case Analyzer API
"""
import requests
import json


class LegalCaseAnalyzerClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def send_message(self, message: str, session_id: str = "test_session"):
        """Send a message to the AI assistant"""
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": message, "session_id": session_id}
        )
        return response.json()
    
    def get_history(self, session_id: str = "test_session"):
        """Get chat history for a session"""
        response = requests.get(f"{self.base_url}/chat/history/{session_id}")
        return response.json()
    
    def clear_history(self, session_id: str = "test_session"):
        """Clear chat history for a session"""
        response = requests.delete(f"{self.base_url}/chat/history/{session_id}")
        return response.json()
    
    def list_sessions(self):
        """List all active sessions"""
        response = requests.get(f"{self.base_url}/chat/sessions")
        return response.json()


def main():
    """Example usage of the client"""
    client = LegalCaseAnalyzerClient()
    
    print("Legal Case Analyzer API Test Client")
    print("=" * 40)
    
    # Test basic conversation
    session_id = "demo_session"
    
    print(f"\n1. Sending first message to session '{session_id}'...")
    response1 = client.send_message(
        "I need help analyzing a contract dispute case where the defendant claims breach of contract.",
        session_id
    )
    print(f"AI Response: {response1['response']}")
    
    print(f"\n2. Sending follow-up message...")
    response2 = client.send_message(
        "What legal precedents should I look for?",
        session_id
    )
    print(f"AI Response: {response2['response']}")
    
    print(f"\n3. Getting conversation history...")
    history = client.get_history(session_id)
    print(f"History: {json.dumps(history, indent=2)}")
    
    print(f"\n4. Listing all sessions...")
    sessions = client.list_sessions()
    print(f"Sessions: {json.dumps(sessions, indent=2)}")
    
    print(f"\n5. Clearing session history...")
    clear_result = client.clear_history(session_id)
    print(f"Clear result: {clear_result}")


if __name__ == "__main__":
    main()
