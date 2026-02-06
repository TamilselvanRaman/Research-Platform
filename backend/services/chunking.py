"""
Text chunking service for splitting documents into processable chunks.
"""
from typing import List, Dict
from config import get_settings
import logging
import re

logger = logging.getLogger(__name__)
settings = get_settings()


class ChunkingService:
    """Text chunking service."""
    
    def __init__(self, chunk_size: int = None, overlap: int = None):
        """
        Initialize chunking service.
        
        Args:
            chunk_size: Target chunk size in tokens (default from config)
            overlap: Overlap between chunks in tokens (default from config)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.overlap = overlap or settings.chunk_overlap
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count (rough approximation: 1 token ≈ 4 characters).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Simple approximation: split by whitespace and punctuation
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def chunk_text(self, text: str, document_id: int = None) -> List[Dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Full document text
            document_id: Optional document ID for reference
            
        Returns:
            List of chunk dictionaries with text, token_count, chunk_index
        """
        # Split text into sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = self.estimate_tokens(sentence)
            
            # If adding sentence exceeds chunk size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "token_count": current_tokens,
                    "document_id": document_id
                })
                
                # Start new chunk with overlap
                # Keep last few sentences for overlap
                overlap_sentences = []
                overlap_tokens = 0
                for sent in reversed(current_chunk):
                    sent_tokens = self.estimate_tokens(sent)
                    if overlap_tokens + sent_tokens <= self.overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_tokens += sent_tokens
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_tokens = overlap_tokens
                chunk_index += 1
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "chunk_index": chunk_index,
                "text": chunk_text,
                "token_count": current_tokens,
                "document_id": document_id
            })
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def chunk_with_page_info(self, pages: List[Dict]) -> List[Dict]:
        """
        Chunk text while preserving page information.
        
        Args:
            pages: List of page dicts with page_number and text
            
        Returns:
            List of chunks with page_number information
        """
        all_chunks = []
        chunk_index = 0
        
        for page in pages:
            page_chunks = self.chunk_text(page["text"])
            
            # Add page number to chunks
            for chunk in page_chunks:
                chunk["chunk_index"] = chunk_index
                chunk["page_number"] = page["page_number"]
                all_chunks.append(chunk)
                chunk_index += 1
        
        return all_chunks


# Singleton instance
_chunking_service = None

def get_chunking_service() -> ChunkingService:
    """Get chunking service instance."""
    global _chunking_service
    if _chunking_service is None:
        _chunking_service = ChunkingService()
    return _chunking_service
