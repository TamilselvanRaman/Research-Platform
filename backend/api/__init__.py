"""API package initialization."""
from api.health import router as health_router
from api.upload import router as upload_router
from api.search import router as search_router

__all__ = [
    "health_router",
    "upload_router",
    "search_router",
]
