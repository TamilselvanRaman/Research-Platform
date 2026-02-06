"""
Qdrant vector database service.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
from config import get_settings
import logging
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorDBService:
    """Qdrant vector database service."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.collection_name = settings.qdrant_collection
        self.dimension = settings.embedding_dimension
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def add_vectors(self, vectors: List[List[float]], payloads: List[Dict]) -> List[str]:
        """
        Add vectors to collection.
        
        Args:
            vectors: List of embedding vectors
            payloads: List of metadata dicts (one per vector)
            
        Returns:
            List of vector IDs
        """
        if len(vectors) != len(payloads):
            raise ValueError("Vectors and payloads must have same length")
        
        # Generate UUIDs for vectors
        vector_ids = [str(uuid.uuid4()) for _ in vectors]
        
        points = [
            PointStruct(
                id=vid,
                vector=vector,
                payload=payload
            )
            for vid, vector, payload in zip(vector_ids, vectors, payloads)
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Added {len(points)} vectors to Qdrant")
        return vector_ids
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict] = None,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filters: Optional filters (e.g., {"document_id": 123})
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with score and payload
        """
        # Build filter if provided
        query_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            query_filter = Filter(must=conditions) if conditions else None
       
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
            score_threshold=score_threshold
        )
        
        # Format results
        formatted = []
        for result in results:
            formatted.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            })
        
        return formatted
    
    def delete_by_document_id(self, document_id: int):
        """Delete all vectors for a document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
        )
        logger.info(f"Deleted vectors for document {document_id}")


# Singleton instance
_vector_db_service = None

def get_vector_db_service() -> VectorDBService:
    """Get vector DB service instance."""
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service
