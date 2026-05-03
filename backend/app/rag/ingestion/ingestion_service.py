"""
Document ingestion service.
Orchestrates the full pipeline: PDF processing → embedding → vector storage.
"""

from app.rag.ingestion.pdf_processor import process_pdf
from app.services import vector_store_service
from app.core.logging import logger


async def ingest_document(file_id: str, file_name: str, pdf_bytes: bytes) -> dict:
    """
    Ingest a PDF document into the RAG pipeline.

    Steps:
        1. Extract and chunk the PDF text
        2. Generate embeddings and store in ChromaDB

    Args:
        file_id: Unique document identifier.
        file_name: Original filename.
        pdf_bytes: Raw PDF content.

    Returns:
        Dict with page_count and chunk_count.
    """
    logger.info(f"Starting ingestion for: {file_name} (id: {file_id})")

    # Step 1: Process PDF → extract pages → chunk text
    chunks, page_count = process_pdf(file_id, file_name, pdf_bytes)

    if not chunks:
        logger.warning(f"No chunks generated for {file_name}")
        return {"page_count": 0, "chunk_count": 0}

    # Step 2: Generate embeddings and store in ChromaDB
    chunk_count = await vector_store_service.add_chunks(chunks)

    logger.info(
        f"Ingestion complete for '{file_name}': "
        f"{page_count} pages, {chunk_count} chunks stored"
    )

    return {
        "page_count": page_count,
        "chunk_count": chunk_count,
    }
