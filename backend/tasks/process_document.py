"""
Document processing task.
"""
from tasks.celery_app import celery_app
from services import (
    get_storage_service,
    get_pdf_parser,
    get_chunking_service,
    get_embedding_service,
    get_vector_db_service,
    get_search_service
)
from models.database import SessionLocal
from models.document import Document, ProcessingStatus
from models.chunk import Chunk
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.process_document")
def process_document_task(self, document_id: int):
    """
    Process uploaded document: parse, chunk, embed, and index.
    
    Args:
        document_id: ID of document to process
    """
    start_time = time.time()
    logger.info(f"Starting processing for document {document_id}")
    
    db = SessionLocal()
    
    try:
        # Get document from database
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found")
            return {"status": "error", "message": "Document not found"}
        
        # Update status to processing
        document.status = ProcessingStatus.PROCESSING
        db.commit()
        
        # Initialize services
        storage = get_storage_service()
        pdf_parser = get_pdf_parser()
        chunking = get_chunking_service()
        embeddings = get_embedding_service()
        vector_db = get_vector_db_service()
        search_engine = get_search_service()
        
        # Download file from storage
        logger.info(f"Downloading file: {document.storage_path}")
        # Extract object name from path (bucket/object_name)
        object_name = document.storage_path.split('/', 1)[1]
        file_bytes = storage.download_file(object_name)
        
        # Parse PDF
        logger.info("Parsing PDF")
        full_text, metadata = pdf_parser.extract_text(file_bytes)
        pages = pdf_parser.extract_text_by_page(file_bytes)
        
        # Update document metadata
        document.page_count = metadata.get("page_count", len(pages))
        if not document.title and metadata.get("title"):
            document.title = metadata["title"]
        
        # Chunk text by page
        logger.info("Chunking text")
        chunks_data = chunking.chunk_with_page_info(pages)
        
        logger.info(f"Created {len(chunks_data)} chunks")
        
        # Generate embeddings in batch
        logger.info("Generating embeddings")
        chunk_texts = [chunk["text"] for chunk in chunks_data]
        embeddings_list = embeddings.encode_batch(chunk_texts, batch_size=32)
        
        # Prepare data for storage
        chunk_records = []
        vector_payloads = []
        search_docs = []
        
        for i, (chunk_data, embedding) in enumerate(zip(chunks_data, embeddings_list)):
            # Create chunk record
            chunk_record = Chunk(
                document_id=document_id,
                chunk_index=chunk_data["chunk_index"],
                text=chunk_data["text"],
                token_count=chunk_data["token_count"],
                page_number=chunk_data.get("page_number")
            )
            chunk_records.append(chunk_record)
            
            # Prepare vector payload
            vector_payloads.append({
                "chunk_id": None,  # Will update after DB insert
                "document_id": document_id,
                "text": chunk_data["text"],
                "page_number": chunk_data.get("page_number"),
                "company": document.company,
                "document_type": document.document_type
            })
            
            # Prepare search document
            search_docs.append({
                "chunk_id": None,  # Will update after DB insert
                "document_id": document_id,
                "text": chunk_data["text"],
                "metadata": {
                    "page_number": chunk_data.get("page_number"),
                    "company": document.company,
                    "document_type": document.document_type,
                    "document_date": document.document_date,
                    "chunk_index": chunk_data["chunk_index"]
                }
            })
        
        # Save chunks to database
        logger.info("Saving chunks to database")
        db.add_all(chunk_records)
        db.flush()  # Get IDs without committing
        
        # Update chunk IDs in payloads
        for i, chunk_record in enumerate(chunk_records):
            vector_payloads[i]["chunk_id"] = chunk_record.id
            search_docs[i]["chunk_id"] = chunk_record.id
        
        # Store vectors in Qdrant
        logger.info("Storing vectors in Qdrant")
        vector_ids = vector_db.add_vectors(embeddings_list, vector_payloads)
        
        # Update chunk records with vector IDs
        for chunk_record, vector_id in zip(chunk_records, vector_ids):
            chunk_record.vector_id = vector_id
        
        # Index in Elasticsearch
        logger.info("Indexing in Elasticsearch")
        for chunk_record, search_doc in zip(chunk_records, search_docs):
            search_id = search_engine.index_chunk(
                chunk_id=search_doc["chunk_id"],
                document_id=search_doc["document_id"],
                text=search_doc["text"],
                metadata=search_doc["metadata"]
            )
            chunk_record.search_id = search_id
        
        # Update document status
        document.status = ProcessingStatus.COMPLETED
        document.chunk_count = len(chunk_records)
        document.processed_at = datetime.utcnow()
        document.processing_time = time.time() - start_time
        
        db.commit()
        
        logger.info(f"Document {document_id} processed successfully in {document.processing_time:.2f}s")
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunks": len(chunk_records),
            "processing_time": document.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}", exc_info=True)
        
        # Update document status to failed
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = ProcessingStatus.FAILED
            document.error_message = str(e)
            db.commit()
        
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()
