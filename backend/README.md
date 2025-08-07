# Legal Case Analyzer Backend

A FastAPI backend with LangGraph integration that provides context-aware LLM interactions for legal case analysis.

## Features

- **Context-Aware Conversations**: Maintains conversation history per session
- **Legal-Focused Tools**: Built-in tools for legal case analysis and precedent search
- **RESTful API**: Clean HTTP endpoints for easy integration
- **Session Management**: Multiple concurrent chat sessions with individual histories
- **LangGraph Integration**: Advanced conversation flow with tool calling capabilities

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Run the Server

```bash
python main.py
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/redoc

## API Endpoints

### POST /chat
Send a message to the AI assistant and receive a response.

### GET /chat/history/{session_id}
Retrieve chat history for a specific session.

### DELETE /chat/history/{session_id}
Clear chat history for a specific session.

### GET /chat/sessions
List all active chat sessions.

## Built-in Tools

1. **analyze_legal_case**: Analyzes legal case details and provides insights
2. **search_legal_precedents**: Searches for relevant legal precedents

## Test Client

Run the test client to see the API in action:

```bash
python test_client.py
```
