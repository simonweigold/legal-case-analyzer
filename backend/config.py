import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # API Configuration
    API_TITLE = "Legal Case Analyzer API"
    API_VERSION = "1.0.0"
    HOST = "0.0.0.0"
    PORT = 8000
    
    # Model Configuration
    MODEL_NAME = "gpt-4o-mini"
    STREAMING = True
    
    # CORS Configuration
    CORS_ORIGINS = ["*"]  # Development: allow all; tighten for production
    CORS_CREDENTIALS = False
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]
    
    # Environment Variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()
