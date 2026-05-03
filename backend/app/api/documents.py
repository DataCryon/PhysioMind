"""
Document management API routes.
Handles PDF upload, listing, and deletion.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services import supabase_service, vector_store_service
from app.rag.ingestion.ingestion_service import ingest_document
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadResponse,
)
from app.utils.helpers import generate_file_id, validate_pdf_file
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document.

    Pipeline:
    1. Validate file type
    2. Upload to Supabase Storage
    3. Extract text, chunk, and embed into ChromaDB
    4. Save metadata to Supabase database
    """
    # Validate PDF
    if not file.filename or not validate_pdf_file(file.filename, file.content_type or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted. Please upload a .pdf file.",
        )

    try:
        # Read file content
        file_bytes = await file.read()
        file_size = len(file_bytes)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty.",
            )

        file_id = generate_file_id()
        file_name = file.filename

        logger.info(f"Processing upload: {file_name} ({file_size} bytes)")

        # Step 1: Upload to Supabase Storage
        storage_path = await supabase_service.upload_pdf(file_id, file_bytes, file_name)

        # Step 2: Ingest into RAG pipeline (extract → chunk → embed → store)
        ingestion_result = await ingest_document(file_id, file_name, file_bytes)

        # Step 3: Save metadata to Supabase database
        metadata = {
            "id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "page_count": ingestion_result["page_count"],
            "chunk_count": ingestion_result["chunk_count"],
            "supabase_path": storage_path,
        }
        await supabase_service.save_metadata(metadata)

        logger.info(f"Upload complete: {file_name} (id: {file_id})")

        return DocumentUploadResponse(
            id=file_id,
            file_name=file_name,
            file_size=file_size,
            page_count=ingestion_result["page_count"],
            chunk_count=ingestion_result["chunk_count"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}",
        )


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """Fetch all uploaded documents with metadata."""
    try:
        documents = await supabase_service.get_all_documents()
        return DocumentListResponse(
            documents=[DocumentResponse(**doc) for doc in documents],
            total=len(documents),
        )
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch documents.",
        )


@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
async def delete_document(file_id: str):
    """
    Delete a document and all its associated data.

    Cleanup:
    1. Delete vectors from ChromaDB
    2. Delete file from Supabase Storage
    3. Delete metadata from Supabase database
    """
    try:
        # Verify document exists
        doc = await supabase_service.get_document_by_id(file_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id '{file_id}' not found.",
            )

        logger.info(f"Deleting document: {doc['file_name']} (id: {file_id})")

        # Step 1: Delete vectors from ChromaDB
        chunks_deleted = await vector_store_service.delete_by_file_id(file_id)

        # Step 2: Delete file from Supabase Storage
        await supabase_service.delete_pdf(doc["supabase_path"])

        # Step 3: Delete metadata
        await supabase_service.delete_metadata(file_id)

        logger.info(
            f"Document deleted: {doc['file_name']} "
            f"({chunks_deleted} chunks removed)"
        )

        return {
            "message": f"Document '{doc['file_name']}' deleted successfully",
            "chunks_deleted": chunks_deleted,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )
