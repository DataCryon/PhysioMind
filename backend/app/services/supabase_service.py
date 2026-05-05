from __future__ import annotations
"""
Supabase service for PDF storage and metadata management.
Handles file uploads/downloads/deletions and metadata CRUD operations.
"""

from supabase import create_client, Client
from app.core.config import get_settings
from app.core.logging import logger

# Module-level client (initialized lazily)
_client: Client | None = None


def get_supabase_client() -> Client:
    """Get or create the Supabase client (singleton)."""
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.error("❌ SUPABASE_URL or SUPABASE_KEY is missing.")
            raise ValueError("Supabase credentials missing. Please set them in environment variables.")
            
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client initialized")
    return _client


async def upload_pdf(file_id: str, file_bytes: bytes, file_name: str) -> str:
    """
    Upload a PDF file to Supabase Storage.

    Returns the storage path of the uploaded file.
    """
    settings = get_settings()
    client = get_supabase_client()
    storage_path = f"{file_id}/{file_name}"

    try:
        client.storage.from_(settings.SUPABASE_BUCKET).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": "application/pdf"},
        )
        logger.info(f"Uploaded PDF to Supabase: {storage_path}")
        return storage_path
    except Exception as e:
        logger.error(f"Failed to upload PDF to Supabase: {e}")
        raise


async def download_pdf(storage_path: str) -> bytes:
    """Download a PDF file from Supabase Storage."""
    settings = get_settings()
    client = get_supabase_client()

    try:
        data = client.storage.from_(settings.SUPABASE_BUCKET).download(storage_path)
        logger.info(f"Downloaded PDF from Supabase: {storage_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to download PDF from Supabase: {e}")
        raise


async def delete_pdf(storage_path: str) -> None:
    """Delete a PDF file from Supabase Storage."""
    settings = get_settings()
    client = get_supabase_client()

    try:
        client.storage.from_(settings.SUPABASE_BUCKET).remove([storage_path])
        logger.info(f"Deleted PDF from Supabase: {storage_path}")
    except Exception as e:
        logger.error(f"Failed to delete PDF from Supabase: {e}")
        raise


def get_public_url(storage_path: str) -> str:
    """Get the public URL for a stored PDF."""
    settings = get_settings()
    client = get_supabase_client()
    return client.storage.from_(settings.SUPABASE_BUCKET).get_public_url(storage_path)


async def save_metadata(doc_data: dict) -> dict:
    """
    Save document metadata to the pdf_documents table.

    Args:
        doc_data: Dictionary with id, file_name, file_size, page_count,
                  chunk_count, supabase_path fields.
    """
    client = get_supabase_client()

    try:
        result = (
            client.table("pdf_documents")
            .insert(doc_data)
            .execute()
        )
        logger.info(f"Saved metadata for document: {doc_data.get('file_name')}")
        return result.data[0] if result.data else doc_data
    except Exception as e:
        logger.error(f"Failed to save document metadata: {e}")
        raise


async def get_all_documents() -> list[dict]:
    """Fetch all document metadata from the pdf_documents table."""
    client = get_supabase_client()

    try:
        result = (
            client.table("pdf_documents")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error(f"Failed to fetch documents: {e}")
        raise


async def get_document_by_id(file_id: str) -> dict | None:
    """Fetch a single document's metadata by ID."""
    client = get_supabase_client()

    try:
        result = (
            client.table("pdf_documents")
            .select("*")
            .eq("id", file_id)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to fetch document {file_id}: {e}")
        raise


async def delete_metadata(file_id: str) -> None:
    """Delete document metadata from the pdf_documents table."""
    client = get_supabase_client()

    try:
        client.table("pdf_documents").delete().eq("id", file_id).execute()
        logger.info(f"Deleted metadata for document: {file_id}")
    except Exception as e:
        logger.error(f"Failed to delete document metadata: {e}")
        raise
