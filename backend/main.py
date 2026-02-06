"""
FastAPI main application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import health_router, upload_router, search_router
from models import init_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Research Intelligence Platform API",
    description="API for document ingestion, processing, and intelligent search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(search_router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Research Intelligence Platform API")
    
    # Initialize database tables
    logger.info("Initializing database")
    init_db()
    
    # Initialize services (triggers lazy loading)
    from services import (
        get_storage_service,
        get_vector_db_service,
        get_search_service,
        get_embedding_service
    )
    
    logger.info("Initializing MinIO storage")
    get_storage_service()
    
    logger.info("Initializing Qdrant vector database")
    get_vector_db_service()
    
    logger.info("Initializing Elasticsearch")
    get_search_service()
    
    # logger.info("Loading embedding model (this may take a minute...)")
    # get_embedding_service()
    
    logger.info("API startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Research Intelligence Platform API")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Research Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    from config import get_settings
    
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
