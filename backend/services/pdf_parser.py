"""
PDF parsing service using PyMuPDF.
"""
import fitz  # PyMuPDF
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """PDF text extraction service."""
    
    @staticmethod
    def extract_text(pdf_bytes: bytes) -> Tuple[str, Dict]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Tuple of (full_text, metadata)
            metadata includes: page_count, title, author, etc.
        """
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Extract text from all pages
            full_text = ""
            page_texts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                page_texts.append(text)
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"
            
            # Extract metadata
            metadata = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", ""),
            }
            
            doc.close()
            
            word_count = len(full_text.split())
            logger.info(f"Extracted {word_count} words from {len(doc)} pages")
            
            return full_text, metadata
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    @staticmethod
    def extract_text_by_page(pdf_bytes: bytes) -> List[Dict]:
        """
        Extract text page by page with metadata.
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            List of dicts with page_number, text, word_count
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                pages.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "word_count": len(text.split()),
                    "char_count": len(text)
                })
            
            doc.close()
            return pages
            
        except Exception as e:
            logger.error(f"Error parsing PDF by page: {e}")
            raise
    
    @staticmethod
    def validate_pdf(pdf_bytes: bytes) -> bool:
        """
        Check if file is a valid PDF.
        
        Args:
            pdf_bytes: File as bytes
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            is_valid = len(doc) > 0
            doc.close()
            return is_valid
        except:
            return False


# Singleton instance
_pdf_parser = None

def get_pdf_parser() -> PDFParser:
    """Get PDF parser instance."""
    global _pdf_parser
    if _pdf_parser is None:
        _pdf_parser = PDFParser()
    return _pdf_parser
