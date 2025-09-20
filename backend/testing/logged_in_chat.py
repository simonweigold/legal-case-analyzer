import requests

BASE_URL = "http://localhost:8000"


def sign_in():
    """Sign in to the backend and return the access token."""
    # Adjust the payload as required by your authentication endpoint
    payload = {
        "username": "admin@admin.com",
        "password": "admin123",
        "grant_type": "password"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data=payload, headers=headers)
    if response.status_code != 200:
        print(f"Sign in failed with status code {response.status_code}: {response.text}")
    response.raise_for_status()
    data = response.json()
    token = data.get("access_token")
    if not token:
        raise Exception("No access token received")
    return token


def chat_message(token, message, conversation_id=None):
    """Send a chat message to the backend. Optionally include a conversation ID to continue an existing conversation."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": message}
    if conversation_id:
        payload["conversation_id"] = conversation_id
    response = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    print("Signing in...")
    token = sign_in()
    print(f"Signed in. Token: {token}\n")

    # Start a new conversation
    conversation_id = None
    
    # Turn 1: Send initial greeting
    print("Turn 1: Sending message 'Hello'")
    response = chat_message(token, "Hello", conversation_id)
    conversation_id = response.get("conversation_id", conversation_id)
    print(f"Response: {response}\n")

    # Turn 2: Continue conversation
    print("Turn 2: Sending message 'How are you?'")
    response = chat_message(token, "How are you?", conversation_id)
    print(f"Response: {response}\n")

    # Turn 3: Ask for a joke
    print("Turn 3: Sending message 'Tell me a joke.'")
    response = chat_message(token, "Tell me a joke.", conversation_id)
    print(f"Response: {response}\n")
    
    # Turn 4: Query conversation history
    print("Turn 4: Sending message 'What was my first message?'")
    response = chat_message(token, "What was my first message?", conversation_id)
    print(f"Response: {response}\n")


if __name__ == "__main__":
    main()
