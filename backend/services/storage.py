"""
MinIO storage service for document files.
"""
from minio import Minio
from minio.error import S3Error
from config import get_settings
import io
from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class StorageService:
    """MinIO storage service."""
    
    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket = settings.minio_bucket
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    def upload_file(self, file_data: BinaryIO, object_name: str, content_type: str = "application/pdf") -> str:
        """
        Upload file to MinIO.
        
        Args:
            file_data: File data as binary stream
            object_name: Object name in bucket
            content_type: MIME type
            
        Returns:
            Object path
        """
        try:
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Reset to beginning
            
            self.client.put_object(
                self.bucket,
                object_name,
                file_data,
                length=file_size,
                content_type=content_type
            )
            
            logger.info(f"Uploaded file: {object_name}, size: {file_size} bytes")
            return f"{self.bucket}/{object_name}"
            
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def download_file(self, object_name: str) -> bytes:
        """
        Download file from MinIO.
        
        Args:
            object_name: Object name in bucket
            
        Returns:
            File data as bytes
        """
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise
    
    def delete_file(self, object_name: str):
        """Delete file from MinIO."""
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(f"Deleted file: {object_name}")
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """
        Get presigned URL for file access.
        
        Args:
            object_name: Object name in bucket
            expires: URL expiration time in seconds
            
        Returns:
            Presigned URL
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket,
                object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise


# Singleton instance
_storage_service = None

def get_storage_service() -> StorageService:
    """Get storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
