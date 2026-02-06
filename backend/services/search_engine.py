"""
Elasticsearch full-text search service.
"""
from elasticsearch import Elasticsearch
from typing import List, Dict, Optional
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchService:
    """Elasticsearch search service."""
    
    def __init__(self):
        """Initialize Elasticsearch client."""
        self.client = Elasticsearch([settings.elasticsearch_url])
        self.index_name = settings.elasticsearch_index
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist."""
        try:
            if not self.client.indices.exists(index=self.index_name):
                logger.info(f"Creating Elasticsearch index: {self.index_name}")
                # Define index mapping
                mappings = {
                    "properties": {
                        "chunk_id": {"type": "integer"},
                        "document_id": {"type": "integer"},
                        "text": {"type": "text"},
                        "company": {"type": "keyword"},
                        "document_type": {"type": "keyword"},
                        "document_date": {"type": "date"},
                        "page_number": {"type": "integer"},
                        "chunk_index": {"type": "integer"}
                    }
                }
                
                self.client.indices.create(index=self.index_name, mappings=mappings)
                logger.info(f"Created Elasticsearch index: {self.index_name}")
            else:
                logger.info(f"Elasticsearch index already exists: {self.index_name}")
        except Exception as e:
            logger.error(f"Error checking/creating Elasticsearch index: {e}")
            # Don't raise if it already exists or other non-critical error
            pass
    
    def index_chunk(self, chunk_id: int, document_id: int, text: str, metadata: Dict) -> str:
        """
        Index a single chunk.
        
        Args:
            chunk_id: Chunk ID from database
            document_id: Document ID
            text: Chunk text
            metadata: Additional metadata (company, document_type, etc.)
            
        Returns:
            Elasticsearch document ID
        """
        doc = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "text": text,
            **metadata
        }
        
        result = self.client.index(index=self.index_name, document=doc)
        return result["_id"]
    
    def index_chunks_batch(self, chunks: List[Dict]) -> int:
        """
        Index multiple chunks in batch.
        
        Args:
            chunks: List of chunk dicts with chunk_id, document_id, text, metadata
            
        Returns:
            Number of indexed documents
        """
        from elasticsearch.helpers import bulk
        
        actions = []
        for chunk in chunks:
            action = {
                "_index": self.index_name,
                "_source": {
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "text": chunk["text"],
                    **chunk.get("metadata", {})
                }
            }
            actions.append(action)
        
        success, failed = bulk(self.client, actions)
        logger.info(f"Indexed {success} chunks, {failed} failed")
        return success
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Full-text search.
        
        Args:
            query: Search query
            limit: Maximum results
            filters: Optional filters (company, document_type, etc.)
            
        Returns:
            List of search results with score and document
        """
        # Build query
        must_clauses = [
            {"match": {"text": {"query": query, "boost": 1.0}}}
        ]
        
        # Add filters
        filter_clauses = []
        if filters:
            if filters.get("company"):
                filter_clauses.append({"term": {"company": filters["company"]}})
            if filters.get("document_type"):
                filter_clauses.append({"term": {"document_type": filters["document_type"]}})
            if filters.get("document_id"):
                filter_clauses.append({"term": {"document_id": filters["document_id"]}})
        
        search_query = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
                }
            },
            "size": limit,
            "highlight": {
                "fields": {
                    "text": {
                        "fragment_size": 150,
                        "number_of_fragments": 1
                    }
                }
            }
        }
        
        results = self.client.search(index=self.index_name, **search_query)
        
        # Format results
        formatted = []
        for hit in results["hits"]["hits"]:
            formatted.append({
                "es_id": hit["_id"],
                "score": hit["_score"],
                "chunk_id": hit["_source"]["chunk_id"],
                "document_id": hit["_source"]["document_id"],
                "text": hit["_source"]["text"],
                "highlighted": hit.get("highlight", {}).get("text", [None])[0],
                "metadata": {
                    k: v for k, v in hit["_source"].items()
                    if k not in ["chunk_id", "document_id", "text"]
                }
            })
        
        return formatted
    
    def delete_by_document_id(self, document_id: int):
        """Delete all chunks for a document."""
        query = {
            "query": {
                "term": {"document_id": document_id}
            }
        }
        self.client.delete_by_query(index=self.index_name, **query)
        logger.info(f"Deleted Elasticsearch docs for document {document_id}")


# Singleton instance
_search_service = None

def get_search_service() -> SearchService:
    """Get search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
