import os
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv(find_dotenv())

# Import modular components
from config import settings
from services.tools import get_tools, get_tools_by_name
from utils.workflow import create_workflow
from routes.chat import router as chat_router

# Initialize the language model
model = ChatOpenAI(model=settings.MODEL_NAME, streaming=settings.STREAMING)

# Setup tools
tools = get_tools()
model = model.bind_tools(tools)
tools_by_name = get_tools_by_name()

# Create the workflow graph
graph = create_workflow(model, tools_by_name)

# Initialize FastAPI app
app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION)

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

# Include chat routes
app.include_router(chat_router)

# Make graph available to routes that need it
app.state.graph = graph

if __name__ == "__main__":
    print(f"Starting {settings.API_TITLE}...")
    print(f"API will be available at: http://localhost:{settings.PORT}")
    print(f"API documentation at: http://localhost:{settings.PORT}/docs")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
