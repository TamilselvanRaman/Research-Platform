"""
Search API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import SearchRequest, SearchResponse, SearchResult, FilterOptions
from models.document import Document
from services import get_hybrid_search_service
from sqlalchemy import func, distinct
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search documents using hybrid vector + keyword search.
    
    Args:
        request: Search request with query and filters
        db: Database session
        
    Returns:
        Search results with relevance scores
    """
    start_time = time.time()
    
    try:
        # Build filters
        filters = {}
        if request.company:
            filters["company"] = request.company
        if request.document_type:
            filters["document_type"] = request.document_type
        
        # Perform hybrid search
        hybrid_search = get_hybrid_search_service()
        results = hybrid_search.search(
            query=request.query,
            limit=request.limit + request.offset,  # Get more for pagination
            filters=filters if filters else None,
            vector_weight=request.hybrid_weight
        )
        
        # Apply pagination
        results = results[request.offset:request.offset + request.limit]
        
        # Get document details for results
        document_ids = list(set(r["document_id"] for r in results))
        documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
        doc_map = {doc.id: doc for doc in documents}
        
        # Format results
        search_results = []
        for result in results:
            doc = doc_map.get(result["document_id"])
            search_results.append(SearchResult(
                chunk_id=result["chunk_id"],
                document_id=result["document_id"],
                document_title=doc.title or doc.original_filename if doc else "Unknown",
                company=result.get("company"),
                text=result["text"],
                score=result["score"],
                page_number=result.get("page_number"),
                highlighted_text=result.get("highlighted_text")
            ))
        
        took_ms = int((time.time() - start_time) * 1000)
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(results),
            took_ms=took_ms
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/filters", response_model=FilterOptions)
async def get_filter_options(db: Session = Depends(get_db)):
    """
    Get available filter options for search.
    
    Args:
        db: Database session
        
    Returns:
        Available companies, document types, and date range
    """
    try:
        # Get unique companies
        companies = db.query(distinct(Document.company))\
            .filter(Document.company.isnot(None))\
            .order_by(Document.company)\
            .all()
        companies = [c[0] for c in companies]
        
        # Get unique document types
        doc_types = db.query(distinct(Document.document_type))\
            .filter(Document.document_type.isnot(None))\
            .order_by(Document.document_type)\
            .all()
        doc_types = [t[0] for t in doc_types]
        
        # Get date range
        date_range = db.query(
            func.min(Document.document_date),
            func.max(Document.document_date)
        ).first()
        
        return FilterOptions(
            companies=companies,
            document_types=doc_types,
            date_range={
                "min": date_range[0].isoformat() if date_range[0] else None,
                "max": date_range[1].isoformat() if date_range[1] else None
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        raise HTTPException(status_code=500, detail=str(e))
