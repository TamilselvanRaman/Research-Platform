"""
Simplified FastAPI demo server that runs without Docker dependencies.
Now includes in-memory storage for uploaded documents.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# In-memory storage for demo mode
documents_store: Dict[int, dict] = {}
document_counter = 0

# Create FastAPI app
app = FastAPI(
    title="Research Intelligence Platform API (Demo Mode)",
    description="Demo API - Docker services not required. Files stored in memory.",
    version="1.0.0-demo",
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


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Research Intelligence Platform API (Demo Mode)")
    logger.info("Note: Running without Docker services - files stored in memory")
    logger.info("API startup complete!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Research Intelligence Platform API (Demo Mode)",
        "version": "1.0.0-demo",
        "docs": "/docs",
        "note": "Running without Docker services. Files are stored in memory."
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "mode": "demo",
        "message": "API is running in demo mode without Docker services"
    }


@app.get("/health/services")
async def health_services():
    """Check all services health."""
    return {
        "status": "partial",
        "services": {
            "api": "healthy",
            "database": "in_memory",
            "qdrant": "not_configured",
            "elasticsearch": "not_configured",
            "minio": "in_memory",
            "redis": "not_configured"
        },
        "message": "Start Docker Compose to enable full persistent storage"
    }


@app.get("/api/documents")
async def list_documents(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """List all uploaded documents."""
    docs = list(documents_store.values())
    
    # Filter by status if provided
    if status:
        docs = [d for d in docs if d.get("status") == status]
    
    # Apply pagination
    paginated = docs[skip:skip + limit]
    
    # Return without the content field (too large)
    result = []
    for doc in paginated:
        doc_copy = {k: v for k, v in doc.items() if k != "content"}
        result.append(doc_copy)
    
    return result


@app.get("/api/documents/{document_id}")
async def get_document(document_id: int):
    """Get document details by ID."""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents_store[document_id]
    # Return without content
    return {k: v for k, v in doc.items() if k != "content"}


@app.get("/api/documents/{document_id}/download")
async def download_document(document_id: int):
    """Download a document."""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents_store[document_id]
    content = doc.get("content")
    
    if not content:
        raise HTTPException(status_code=404, detail="Document content not available")
    
    # Return as downloadable PDF
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{doc["original_filename"]}"'
        }
    )


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document."""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    del documents_store[document_id]
    logger.info(f"Deleted document: ID={document_id}")
    
    return {"message": "Document deleted successfully"}


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and store document in memory."""
    global document_counter
    
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read and store file content
    content = await file.read()
    file_size = len(content)
    
    # Increment counter and create document
    document_counter += 1
    doc_id = document_counter
    
    documents_store[doc_id] = {
        "id": doc_id,
        "filename": f"{doc_id}_{file.filename}",
        "original_filename": file.filename,
        "file_size": file_size,
        "mime_type": file.content_type,
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "chunk_count": 0,
        "content": content  # Store actual content for download
    }
    
    logger.info(f"Demo upload stored: {file.filename} ({file_size} bytes) -> ID={doc_id}")
    
    return {
        "document_id": doc_id,
        "filename": file.filename,
        "status": "completed",
        "message": "File uploaded and stored in memory (demo mode)"
    }


@app.post("/api/search")
async def search(request: dict):
    """Search documents (demo - basic text matching)."""
    query = request.get("query", "")
    
    if not query:
        return {"results": [], "total": 0, "query": query}
    
    # Simple search through document filenames
    results = []
    for doc in documents_store.values():
        if query.lower() in doc["original_filename"].lower():
            results.append({
                "document_id": doc["id"],
                "filename": doc["original_filename"],
                "text": f"Document: {doc['original_filename']}",
                "score": 1.0
            })
    
    return {
        "results": results,
        "total": len(results),
        "query": query,
        "message": "Basic filename search (demo mode)"
    }


@app.get("/api/search/filters")
async def get_filters():
    """Get available search filters."""
    return {
        "companies": [],
        "document_types": [],
        "date_range": {"min": None, "max": None}
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("Starting in DEMO MODE (without Docker)")
    logger.info("Files will be stored IN MEMORY (lost on restart)")
    logger.info("To enable full persistent storage:")
    logger.info("1. Start Docker Desktop")
    logger.info("2. Run: docker-compose up -d")
    logger.info("3. Run: python main.py (instead of demo_main.py)")
    logger.info("=" * 60)
    
    uvicorn.run(
        "demo_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
