"""
Document model - represents uploaded documents.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float
from sqlalchemy.sql import func
from models.database import Base
import enum


class ProcessingStatus(str, enum.Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """Document model."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(512), nullable=False)
    original_filename = Column(String(512), nullable=False)
    
    # Metadata
    title = Column(String(512))
    company = Column(String(256), index=True)
    document_type = Column(String(128), index=True)
    document_date = Column(DateTime, index=True)
    
    # File info
    file_size = Column(Integer)  # bytes
    mime_type = Column(String(128))
    page_count = Column(Integer)
    
    # Storage
    storage_path = Column(String(1024), nullable=False)  # MinIO path
    
    # Processing
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING, index=True)
    error_message = Column(Text)
    
    # Statistics
    chunk_count = Column(Integer, default=0)
    processing_time = Column(Float)  # seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"
