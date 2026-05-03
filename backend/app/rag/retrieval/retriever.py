"""
Document retrieval module.
Queries the vector store for relevant chunks based on user questions.
"""

from app.services import vector_store_service
from app.core.config import get_settings
from app.core.logging import logger


async def retrieve_relevant_chunks(
    query: str, top_k: int | None = None, file_id: str | None = None
) -> list[dict]:
    """
    Retrieve the most relevant document chunks for a given query.

    Performs similarity search in Supabase and returns deduplicated,
    ranked results with full metadata for source attribution.

    Args:
        query: User's question text.
        top_k: Number of top results to retrieve.
        file_id: Optional ID of a specific PDF to search within.
    """
    settings = get_settings()
    k = top_k or settings.TOP_K

    chunks = await vector_store_service.query_similar(query, top_k=k, file_id=file_id)

    if not chunks:
        logger.info("No relevant chunks found for query")
        return []

    # Sort by distance (lower = more similar for cosine)
    chunks.sort(key=lambda c: c["distance"])

    logger.info(
        f"Retrieved {len(chunks)} chunks | "
        f"Best score: {chunks[0]['distance']:.4f} | "
        f"Sources: {set(c['file_name'] for c in chunks)}"
    )

    return chunks
