"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from models.document import ProcessingStatus


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    title: Optional[str] = None
    company: Optional[str] = None
    document_type: Optional[str] = None
    document_date: Optional[datetime] = None


class DocumentCreate(DocumentBase):
    """Document creation schema."""
    pass


class DocumentResponse(DocumentBase):
    """Document response schema."""
    id: int
    original_filename: str
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    status: ProcessingStatus
    chunk_count: int = 0
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


# Search Schemas
class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., min_length=1, max_length=500)
    company: Optional[str] = None
    document_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    hybrid_weight: float = Field(default=0.7, ge=0.0, le=1.0)  # Weight for vector search


class SearchResult(BaseModel):
    """Individual search result."""
    chunk_id: int
    document_id: int
    document_title: str
    company: Optional[str] = None
    text: str
    score: float
    page_number: Optional[int] = None
    highlighted_text: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: List[SearchResult]
    total: int
    took_ms: int  # Query execution time


# Upload Response
class UploadResponse(BaseModel):
    """File upload response."""
    document_id: int
    filename: str
    status: str
    message: str


# Health Check
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    services: dict


# Filter Options
class FilterOptions(BaseModel):
    """Available filter options."""
    companies: List[str]
    document_types: List[str]
    date_range: dict
