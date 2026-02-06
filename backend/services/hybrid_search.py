"""
Hybrid search service combining vector and keyword search.
"""
from typing import List, Dict, Optional
from services.vector_db import get_vector_db_service
from services.search_engine import get_search_service
from services.embeddings import get_embedding_service
import logging

logger = logging.getLogger(__name__)


class HybridSearchService:
    """Hybrid search combining vector similarity and keyword search."""
    
    def __init__(self):
        """Initialize hybrid search service."""
        self.vector_db = get_vector_db_service()
        self.search_engine = get_search_service()
        self.embeddings = get_embedding_service()
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None,
        vector_weight: float = 0.7
    ) -> List[Dict]:
        """
        Perform hybrid search.
        
        Args:
            query: Search query text
            limit: Maximum results to return
            filters: Optional filters (company, document_type, etc.)
            vector_weight: Weight for vector search (0-1), keyword gets (1-weight)
            
        Returns:
            List of search results sorted by combined score
        """
        logger.info(f"Hybrid search query: '{query}', limit: {limit}, vector_weight: {vector_weight}")
        
        # Generate query embedding
        query_embedding = self.embeddings.encode_text(query)
        
        # Perform vector search
        vector_results = self.vector_db.search(
            query_vector=query_embedding,
            limit=limit * 2,  # Get more results for better ranking
            filters=filters
        )
        
        # Perform keyword search
        keyword_results = self.search_engine.search(
            query=query,
            limit=limit * 2,
            filters=filters
        )
        
        # Combine results
        combined = self._combine_results(
            vector_results,
            keyword_results,
            vector_weight
        )
        
        # Sort by combined score and limit
        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined[:limit]
    
    def _combine_results(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict],
        vector_weight: float
    ) -> List[Dict]:
        """
        Combine and score results from both search methods.
        
        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search
            vector_weight: Weight for vector scores
            
        Returns:
            Combined and scored results
        """
        keyword_weight = 1.0 - vector_weight
        
        # Normalize scores to 0-1 range
        vector_results = self._normalize_scores(vector_results)
        keyword_results = self._normalize_scores(keyword_results)
        
        # Create lookup by chunk_id
        results_map = {}
        
        # Add vector results
        for result in vector_results:
            chunk_id = result["payload"]["chunk_id"]
            results_map[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": result["payload"]["document_id"],
                "text": result["payload"]["text"],
                "vector_score": result["score"],
                "keyword_score": 0.0,
                "metadata": {
                    k: v for k, v in result["payload"].items()
                    if k not in ["chunk_id", "document_id", "text"]
                }
            }
        
        # Add/update with keyword results
        for result in keyword_results:
            chunk_id = result["chunk_id"]
            if chunk_id in results_map:
                results_map[chunk_id]["keyword_score"] = result["score"]
                results_map[chunk_id]["highlighted"] = result.get("highlighted")
            else:
                results_map[chunk_id] = {
                    "chunk_id": chunk_id,
                    "document_id": result["document_id"],
                    "text": result["text"],
                    "vector_score": 0.0,
                    "keyword_score": result["score"],
                    "highlighted": result.get("highlighted"),
                    "metadata": result.get("metadata", {})
                }
        
        # Calculate combined scores
        combined_results = []
        for chunk_id, result in results_map.items():
            combined_score = (
                result["vector_score"] * vector_weight +
                result["keyword_score"] * keyword_weight
            )
            
            combined_results.append({
                "chunk_id": chunk_id,
                "document_id": result["document_id"],
                "text": result["text"],
                "score": combined_score,
                "vector_score": result["vector_score"],
                "keyword_score": result["keyword_score"],
                "highlighted_text": result.get("highlighted"),
                **result["metadata"]
            })
        
        return combined_results
    
    @staticmethod
    def _normalize_scores(results: List[Dict]) -> List[Dict]:
        """
        Normalize scores to 0-1 range using min-max normalization.
        
        Args:
            results: List of results with 'score' field
            
        Returns:
            Results with normalized scores
        """
        if not results:
            return results
        
        scores = [r["score"] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        
        # Avoid division by zero
        if max_score - min_score < 1e-10:
            for result in results:
                result["score"] = 1.0
            return results
        
        # Normalize
        for result in results:
            result["score"] = (result["score"] - min_score) / (max_score - min_score)
        
        return results


# Singleton instance
_hybrid_search_service = None

def get_hybrid_search_service() -> HybridSearchService:
    """Get hybrid search service instance."""
    global _hybrid_search_service
    if _hybrid_search_service is None:
        _hybrid_search_service = HybridSearchService()
    return _hybrid_search_service
