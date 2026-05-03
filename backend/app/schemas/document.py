"""
Pydantic schemas for document-related API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Response schema for a single document."""

    id: str
    file_name: str
    file_size: int
    page_count: int = 0
    chunk_count: int = 0
    supabase_path: str = ""
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response schema for listing documents."""

    documents: list[DocumentResponse]
    total: int


class DocumentUploadResponse(BaseModel):
    """Response schema after successful upload."""

    id: str
    file_name: str
    file_size: int
    page_count: int
    chunk_count: int
    message: str = "Document uploaded and processed successfully"
