import os
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

def get_llm(model: Optional[str] = None):
    """
    Return a ChatOpenAI instance. If `model` is provided, use it; otherwise fallback to env var or default.
    """
    selected = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
    return ChatOpenAI(model=selected, temperature=0)

# Default LLM instance for tools
llm = get_llm()

class Settings:
    # API Configuration
    API_TITLE = "Legal Case Analyzer API"
    API_VERSION = "1.0.0"
    HOST = "0.0.0.0"
    PORT = 8000
    
    # Model Configuration
    MODEL_NAME = "gpt-5-nano"
    STREAMING = True
    
    # CORS Configuration - Optimized for development
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    CORS_CREDENTIALS = True
    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["*"]
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./legal_analyzer.db")
    
    # Authentication Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_LIFETIME_SECONDS = 3600
    
    # Environment Variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()
