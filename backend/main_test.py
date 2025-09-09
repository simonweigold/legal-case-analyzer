"""
Minimal test version of main.py to check authentication setup
"""
import os
from contextlib import asynccontextmanager
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables first
load_dotenv(find_dotenv())

# Import configuration
from config import settings

# Import for database initialization
from database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    await create_db_and_tables()
    yield


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE, 
    version=settings.API_VERSION,
    lifespan=lifespan
)

# CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

@app.get("/")
async def root():
    return {"message": settings.API_TITLE, "version": settings.API_VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Only include auth routes for testing
try:
    from routes.auth import router as auth_router
    app.include_router(auth_router)
    print("✅ Auth routes loaded successfully")
except Exception as e:
    print(f"❌ Error loading auth routes: {e}")

if __name__ == "__main__":
    print(f"Starting {settings.API_TITLE} (minimal test version)...")
    print(f"API will be available at: http://localhost:{settings.PORT}")
    print(f"API documentation at: http://localhost:{settings.PORT}/docs")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
