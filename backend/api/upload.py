"""
Document upload and management API endpoints.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from models.document import Document, ProcessingStatus
from models.schemas import DocumentResponse, UploadResponse
from services import get_storage_service
from tasks.process_document import process_document_task
from typing import List
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF document for processing.
    
    Args:
        file: PDF file to upload
        db: Database session
        
    Returns:
        Upload response with document ID and status
    """
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Generate unique filename
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Upload to storage
        storage = get_storage_service()
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create BytesIO object for upload
        from io import BytesIO
        file_stream = BytesIO(file_content)
        
        storage_path = storage.upload_file(
            file_data=file_stream,
            object_name=unique_filename,
            content_type=file.content_type
        )
        
        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_size=file_size,
            mime_type=file.content_type,
            storage_path=storage_path,
            status=ProcessingStatus.PENDING
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Trigger async processing
        process_document_task.delay(document.id)
        
        logger.info(f"Document uploaded: ID={document.id}, filename={file.filename}")
        
        return UploadResponse(
            document_id=document.id,
            filename=file.filename,
            status="processing",
            message="Document uploaded successfully and is being processed"
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    List all documents with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        status: Filter by processing status
        db: Database session
        
    Returns:
        List of documents
    """
    query = db.query(Document)
    
    if status:
        try:
            status_enum = ProcessingStatus(status)
            query = query.filter(Document.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return documents


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get document by ID.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Document details
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get presigned URL for document download.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Presigned download URL
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        storage = get_storage_service()
        object_name = document.storage_path.split('/', 1)[1]
        url = storage.get_file_url(object_name, expires=3600)
        
        return {"url": url, "filename": document.original_filename}
        
    except Exception as e:
        logger.error(f"Error generating download URL: {e}")
        raise HTTPException(status_code=500, detail="Error generating download URL")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete document and all associated data.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Success message
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete from storage
        storage = get_storage_service()
        object_name = document.storage_path.split('/', 1)[1]
        storage.delete_file(object_name)
        
        # Delete from vector DB
        from services import get_vector_db_service, get_search_service
        vector_db = get_vector_db_service()
        vector_db.delete_by_document_id(document_id)
        
        # Delete from Elasticsearch
        search = get_search_service()
        search.delete_by_document_id(document_id)
        
        # Delete from database (cascades to chunks)
        db.delete(document)
        db.commit()
        
        logger.info(f"Document deleted: ID={document_id}")
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
