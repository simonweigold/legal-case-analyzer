# Legal Case Analyzer

Legal case analyzer agent based on the [CoLD case analyzer](https://github.com/Choice-of-Law-Dataverse/cold-case-analysis) but for an application in more fields of law.

## 🚀 Features

- **🤖 LangGraph AI Agent**: Advanced conversational AI with state management and tool calling
- **⚖️ Legal-Specific Tools**: Case search, document analysis, and timeline calculation
- **💾 Persistent Memory**: SQLite database for conversation history and state persistence
- **🔧 FastAPI Backend**: High-performance async API with automatic documentation
- **📊 Checkpointing**: Advanced conversation state management with LangGraph
- **🔍 Multi-Tool Integration**: Extensible tool system for various legal tasks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   FastAPI       │───▶│   LangGraph     │
│   (Future)      │    │   Backend       │    │   AI Agent      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   SQLite DB     │    │     Tools       │
                       │   (Persistent   │    │   - Case Search │
                       │    Memory)      │    │   - Doc Analysis│
                       └─────────────────┘    │   - Timeline    │
                                              └─────────────────┘
```

## 📁 Project Structure

```
legal-case-analyzer/
├── README.md                    # This file
├── backend/                     # FastAPI + LangGraph backend
│   ├── main.py                 # FastAPI application
│   ├── agent.py                # LangGraph AI agent
│   ├── tools.py                # Available tools
│   ├── database.py             # Database models
│   ├── services.py             # Business logic
│   ├── schemas.py              # Pydantic models
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── setup.bat/.sh          # Setup scripts
│   ├── run_dev.py             # Development server
│   ├── test_client.py         # Test client
│   └── README.md              # Backend documentation
└── frontend/                   # Frontend (Future)
    └── (Coming Soon)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Git

### 1. Clone Repository

```bash
git clone https://github.com/simonweigold/legal-case-analyzer.git
cd legal-case-analyzer
```

### 2. Setup Backend

**Windows:**
```cmd
cd backend
setup.bat
```

**Unix/Linux/Mac:**
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### 3. Configure Environment

Edit `backend/.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./conversations.db
APP_NAME=Legal Case Analyzer AI Agent
DEBUG=True
```

### 4. Run the System

```bash
cd backend
python run_dev.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. Test the Agent

```bash
cd backend
python test_client.py
```

## 🔧 Available Tools

### 1. 🔍 Legal Case Search
Search for legal cases and precedents using DuckDuckGo with legal-specific queries.

**Example**: "Search for recent intellectual property cases involving software patents"

### 2. 📄 Document Analysis
Analyze legal documents for summaries, key points, risks, and recommendations.

**Example**: "Analyze this contract clause for potential risks"

### 3. ⏰ Case Timeline Calculator
Calculate typical timelines for different types of legal cases (civil, criminal, family, corporate).

**Example**: "Calculate timeline for a corporate merger case starting January 1st"

## 📚 API Usage Examples

### Create Conversation and Send Message

```python
import httpx
import asyncio

async def chat_with_agent():
    async with httpx.AsyncClient() as client:
        # Create conversation
        conv_response = await client.post("http://localhost:8000/conversations", json={
            "metadata": {"case_type": "intellectual_property"}
        })
        conversation_id = conv_response.json()["conversation_id"]
        
        # Send message
        chat_response = await client.post("http://localhost:8000/chat", json={
            "message": "Search for recent AI patent cases and analyze trends",
            "conversation_id": conversation_id
        })
        
        print(chat_response.json()["response"])

asyncio.run(chat_with_agent())
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/

# Create conversation
curl -X POST "http://localhost:8000/conversations" \
     -H "Content-Type: application/json" \
     -d '{"metadata": {"case_type": "contract"}}'

# Send message
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Analyze this contract clause for risks: The party agrees to unlimited liability",
       "conversation_id": "your-conversation-id"
     }'

# Get conversation history
curl http://localhost:8000/conversations/your-conversation-id

# List available tools
curl http://localhost:8000/tools
```

## 🛠️ Development

### Backend Development

The backend is built with:
- **FastAPI**: Modern async web framework
- **LangGraph**: Advanced AI agent framework with state management
- **SQLAlchemy**: Async ORM for database operations
- **Pydantic**: Data validation and settings
- **OpenAI**: Language model integration

### Adding New Tools

1. Define tool in `backend/tools.py`:
```python
@tool
def new_legal_tool(parameter: str) -> str:
    """Tool description for the AI agent"""
    # Implementation
    return result
```

2. Add to TOOLS list in `backend/tools.py`

3. The agent will automatically discover and use the new tool

### Database Schema

The system uses SQLite with two main tables:
- **conversations**: Stores conversation metadata and timestamps
- **messages**: Stores all messages with role, content, and metadata

## 🔒 Security & Production

### Security Features
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration
- Environment-based configuration

### Production Deployment
1. Set `DEBUG=False`
2. Use production WSGI server (Gunicorn + Uvicorn)
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Implement rate limiting
6. Monitor API performance

## 📊 Monitoring

The system includes:
- Structured logging for all operations
- Error tracking and handling
- Health check endpoints
- Conversation history tracking
- Tool usage analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code structure and patterns
- Add comprehensive docstrings and type hints
- Include error handling for all operations
- Test new features thoroughly
- Update documentation for new features

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For support, questions, or feature requests:
1. Check the [Backend README](backend/README.md) for detailed documentation
2. Create an issue in this repository
3. Review the API documentation at http://localhost:8000/docs when running

## 🔮 Roadmap

## Requirements

### Backend
Top Priority:
- [ ] LangGraph running on FastAPI
- [ ] Chat context memory with SQLite
- [ ] Tools (e.g. Summarization, Number extraction, ...)
  - [ ] Law-Lookup (e.g. swiss law, etc.)
- [ ] Implement tools from: https://github.com/Choice-of-Law-Dataverse/cold-case-analysis/tree/main/cold_case_analyzer_agent/streamlit/tools
Nice to have:
- [ ] Frontend web application
- [ ] Additional legal research tools
- [ ] Document upload and processing
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with legal databases
- [ ] User authentication system
- [ ] API rate limiting and quotas

---

Built with ❤️ for the legal community using cutting-edge AI technology.

## 🐳 Deployment with Docker (Backend + Frontend Single Container)

This project can be built into a single container image that serves the FastAPI backend and the built React (Vite) frontend.

### 1. Build Image

```bash
docker build -t legal-case-analyzer:latest .
```

### 2. Run Container

```bash
docker run --rm -p 8000:8000 \
    -e OPENAI_API_KEY=your_key_here \
    legal-case-analyzer:latest
```

### 3. Access Application

- API root info: http://localhost:8000/
- API docs (Swagger): http://localhost:8000/docs
- Frontend (SPA): http://localhost:8000/app
- Static assets: http://localhost:8000/static/

### 4. Persisting the Database (Optional)

By default the SQLite file lives inside the container. To persist data across runs:

```bash
docker run --rm -p 8000:8000 \
    -e OPENAI_API_KEY=your_key_here \
    -v $(pwd)/backend/legal_analyzer.db:/app/backend/legal_analyzer.db \
    legal-case-analyzer:latest
```

### 5. Customizing Build

- Modify `OPENAI_API_KEY` or other env vars using `-e VAR=value`.
- For production you can add a multi-stage optimization or pin dependencies further.

### 6. Notes

- The frontend is built once during the image build (Vite → `frontend/dist`).
- FastAPI serves the SPA under `/app` to avoid changing the existing root JSON endpoint.
- Minimal code changes were introduced: a small static mount in `backend/main.py`.

---
