"""
Health check API endpoints.
"""
from fastapi import APIRouter
from models.schemas import HealthResponse
from services import (
    get_vector_db_service,
    get_search_service,
    get_storage_service
)
from models.database import SessionLocal
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check."""
    return HealthResponse(
        status="healthy",
        services={}
    )


@router.get("/services", response_model=HealthResponse)
async def health_check_services():
    """Check health of all dependent services."""
    services = {}
    overall_status = "healthy"
    
    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        services["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services["database"] = "unhealthy"
        overall_status = "degraded"
    
    # Check Qdrant
    try:
        vector_db = get_vector_db_service()
        collections = vector_db.client.get_collections()
        services["qdrant"] = "healthy"
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        services["qdrant"] = "unhealthy"
        overall_status = "degraded"
    
    # Check Elasticsearch
    try:
        search = get_search_service()
        search.client.cluster.health()
        services["elasticsearch"] = "healthy"
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        services["elasticsearch"] = "unhealthy"
        overall_status = "degraded"
    
    # Check MinIO
    try:
        storage = get_storage_service()
        storage.client.bucket_exists(storage.bucket)
        services["minio"] = "healthy"
    except Exception as e:
        logger.error(f"MinIO health check failed: {e}")
        services["minio"] = "unhealthy"
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        services=services
    )
