"""
PDF processing module.
Extracts text from PDFs page-wise and chunks it for embedding.
"""

import io
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import get_settings
from app.core.logging import logger


def extract_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    """
    Extract text from each page of a PDF.

    Args:
        pdf_bytes: Raw PDF file content.

    Returns:
        List of (page_number, page_text) tuples. Page numbers are 1-indexed.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []

    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:  # Skip empty pages
            pages.append((idx + 1, text))

    logger.info(f"Extracted {len(pages)} pages with text from PDF ({len(reader.pages)} total pages)")
    return pages


def chunk_text(text: str, chunk_size: int | None = None, chunk_overlap: int | None = None) -> list[str]:
    """
    Split text into overlapping chunks for embedding.

    Uses RecursiveCharacterTextSplitter for intelligent splitting
    that preserves sentence and paragraph boundaries.
    """
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def process_pdf(file_id: str, file_name: str, pdf_bytes: bytes) -> tuple[list[dict], int]:
    """
    Full PDF processing pipeline: extract → chunk → build metadata.

    Args:
        file_id: Unique identifier for the document.
        file_name: Original filename of the PDF.
        pdf_bytes: Raw PDF file content.

    Returns:
        Tuple of (chunks_list, page_count) where each chunk is a dict with:
        - text, file_id, file_name, page_number, chunk_id
    """
    # Extract text page-by-page
    pages = extract_pages(pdf_bytes)

    if not pages:
        logger.warning(f"No text content found in PDF: {file_name}")
        return [], 0

    # Chunk each page and build metadata
    chunks = []
    chunk_counter = 0

    for page_number, page_text in pages:
        page_chunks = chunk_text(page_text)

        for chunk_text_content in page_chunks:
            chunk_counter += 1
            chunks.append({
                "text": chunk_text_content,
                "file_id": file_id,
                "file_name": file_name,
                "page_number": page_number,
                "chunk_id": f"{file_id}_chunk_{chunk_counter}",
            })

    page_count = len(pages)
    logger.info(
        f"Processed PDF '{file_name}': {page_count} pages, {len(chunks)} chunks"
    )
    return chunks, page_count
