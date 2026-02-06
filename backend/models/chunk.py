"""
Chunk model - represents text chunks extracted from documents.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from models.database import Base


class Chunk(Base):
    """Text chunk model."""
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Chunk info
    chunk_index = Column(Integer, nullable=False)  # Order within document
    text = Column(Text, nullable=False)
    token_count = Column(Integer)
    
    # Position in original document
    page_number = Column(Integer)
    start_char = Column(Integer)
    end_char = Column(Integer)
    
    # Vector embedding ID (stored in Qdrant)
    vector_id = Column(String(128), unique=True, index=True)
    
    # Elasticsearch document ID
    search_id = Column(String(128), index=True)
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"
