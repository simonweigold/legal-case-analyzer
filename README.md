# Legal Case Analyzer

AI-assisted legal case analysis. FastAPI backend with LangGraph agent and SQLite persistence. Frontend (Vite/React).

## What is this?
- Backend: FastAPI + LangGraph agent, tools for legal tasks, SQLite for state.
- Frontend: Vite/React.
- Goal: Analyze legal issues and chat with tool-augmented AI.

## Quick start
```bash
# Clone
git clone https://github.com/simonweigold/legal-case-analyzer.git
cd legal-case-analyzer

# Backend setup (macOS/Linux)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure
echo "OPENAI_API_KEY=YOUR_KEY" > .env

# Run
python main.py
```

API docs: http://localhost:8000/docs

## Docker (optional)
```bash
docker build -t legal-case-analyzer:latest .
docker run --rm -p 8000:8000 -e OPENAI_API_KEY=YOUR_KEY legal-case-analyzer:latest
```

## Minimal structure
- backend/: FastAPI app, agent, tools, DB
- frontend/: Vite/React app
- data/: sample cases

## Config
- OPENAI_API_KEY: required
- DATABASE_URL: sqlite (default) or external

## Status
- Features: chat, tools, persistence
- Placeholders: detailed tool list, deployment docs, auth
