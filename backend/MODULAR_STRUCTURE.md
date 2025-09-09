# FastAPI Backend Modular Structure

## Directory Structure

```
backend/
├── main.py                 # Main FastAPI application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── schemas/
│   ├── __init__.py
│   └── chat.py            # Pydantic models for API requests/responses
├── routes/
│   ├── __init__.py
│   └── chat.py            # Chat-related API endpoints
├── services/
│   ├── __init__.py
│   ├── tools.py           # LangChain tools for legal analysis
│   └── session.py         # Session storage management
└── utils/
    ├── __init__.py
    └── workflow.py         # LangGraph workflow utilities
```

## Module Descriptions

### `main.py`
- Entry point for the FastAPI application
- Initializes the app, middleware, and routes
- Sets up the LangChain model and workflow
- Minimal and clean, focusing only on app setup

### `config.py`
- Centralized configuration management
- Environment variables and app settings
- Easy to modify without touching core logic

### `schemas/chat.py`
- Pydantic models for API validation
- `ChatRequest`, `ChatResponse`, `StreamChatRequest`, `ChatHistory`
- Clear separation of data models

### `routes/chat.py`
- All chat-related API endpoints
- `/chat`, `/chat/stream`, `/chat/history/{session_id}`, etc.
- Depends on services for business logic

### `services/tools.py`
- LangChain tools for legal case analysis
- `analyze_legal_case`, `search_legal_precedents`
- Utility functions to get tools and tools_by_name

### `services/session.py`
- Session storage management
- Functions to get, update, clear sessions
- Abstraction for future database integration

### `utils/workflow.py`
- LangGraph workflow utilities
- `AgentState`, workflow creation functions
- Tool node and model calling logic

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a clear responsibility
2. **Maintainability**: Easy to find and modify specific functionality
3. **Scalability**: Easy to add new routes, services, or tools
4. **Testing**: Each module can be tested independently
5. **Reusability**: Services and utilities can be reused across routes
6. **Configuration**: Centralized settings management

## Usage

To run the application:
```bash
cd backend
python main.py
```

The modular structure maintains all the original functionality while providing a much cleaner and more maintainable codebase.
