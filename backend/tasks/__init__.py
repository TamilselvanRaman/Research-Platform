"""Tasks package initialization."""
from tasks.celery_app import celery_app
from tasks.process_document import process_document_task

__all__ = [
    "celery_app",
    "process_document_task",
]
