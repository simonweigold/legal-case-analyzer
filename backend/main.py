import os
from contextlib import asynccontextmanager
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables first
load_dotenv(find_dotenv())

# Setup logging
from logging_config import setup_logging
logger = setup_logging()

# Import configuration
from config import settings

# Import for database initialization
from database.database import create_db_and_tables


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
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        from database.database import async_session_maker
        from sqlalchemy import text
        
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "database": "disconnected",
            "error": str(e)
        }

# Import and setup after app creation to avoid circular imports
def setup_routes_and_dependencies():
    from langchain_openai import ChatOpenAI
    from tools.tools import get_tools, get_tools_by_name
    from tools.streaming_tools import get_streaming_tools, get_streaming_tools_by_name
    from utils.workflow import create_workflow
    from routes.auth import router as auth_router
    from routes.conversations import router as conversations_router
    from routes.chat import router as chat_router, set_model_and_tools
    from routes.tools import router as tools_router
    
    # Initialize the language model
    model = ChatOpenAI(model=settings.MODEL_NAME, streaming=settings.STREAMING)
    
    # Setup tools - combine regular and streaming tools
    regular_tools = get_tools()
    streaming_tools = get_streaming_tools()
    all_tools = regular_tools + streaming_tools
    
    model = model.bind_tools(all_tools)
    
    # Combine tool dictionaries
    regular_tools_by_name = get_tools_by_name()
    streaming_tools_by_name = get_streaming_tools_by_name()
    tools_by_name = {**regular_tools_by_name, **streaming_tools_by_name}
    
    # Set model and tools for chat routes
    set_model_and_tools(model, tools_by_name)
    
    # Create the workflow graph
    graph = create_workflow(model, tools_by_name)
    
    # Make graph available to routes that need it
    app.state.graph = graph
    
    # Include routes
    app.include_router(auth_router)
    app.include_router(conversations_router)
    app.include_router(chat_router)
    app.include_router(tools_router)

# Setup routes and dependencies
setup_routes_and_dependencies()

# --- Static Frontend Mount (minimal addition) ---
# If a built frontend (Vite) "dist" directory exists at ../frontend/dist, serve it.
frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist_path):
    # Mount static files under /static and serve index.html at root for SPA routing (except API routes)
    app.mount("/static", StaticFiles(directory=frontend_dist_path, html=True), name="static")

    @app.get("/app", include_in_schema=False)
    async def serve_index():  # explicit route
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))

    # Fallback for SPA routes that don't start with /api or known prefixes; keeps existing root JSON endpoint.
    # We avoid overriding existing '/' root path returning API info; users access SPA via /app.

if __name__ == "__main__":
    print(f"Starting {settings.API_TITLE}...")
    print(f"API will be available at: http://localhost:{settings.PORT}")
    print(f"API documentation at: http://localhost:{settings.PORT}/docs")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
