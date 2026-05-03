"""
Supabase Vector (pgvector) service.
Manages document chunk embeddings with persistent cloud storage.
"""

from __future__ import annotations
from typing import Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.supabase import SupabaseVectorStore
from app.core.config import get_settings
from app.core.logging import logger
from app.services.supabase_service import get_supabase_client

# Module-level singletons
_vector_store: SupabaseVectorStore | None = None
_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Get or create the embeddings model (singleton, cached)."""
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True, "batch_size": 32},
        )
        logger.info("Embedding model loaded successfully")
    return _embeddings


def _get_vector_store() -> SupabaseVectorStore:
    """Get or create the Supabase Vector Store (singleton)."""
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        supabase_client = get_supabase_client()
        embeddings = get_embeddings()
        
        _vector_store = SupabaseVectorStore(
            client=supabase_client,
            embedding=embeddings,
            table_name=settings.SUPABASE_VECTOR_TABLE,
            query_name="match_chunks",
        )
        logger.info(f"Supabase Vector Store initialized (table: {settings.SUPABASE_VECTOR_TABLE})")
    return _vector_store


def initialize() -> None:
    """Pre-initialize embeddings and Vector Store on startup."""
    get_embeddings()
    _get_vector_store()
    logger.info("Vector store service initialized")


async def add_chunks(chunks: list[dict]) -> int:
    """
    Add document chunks to Supabase Vector Store.

    Args:
        chunks: List of dicts with keys:
            - text: str (chunk content)
            - file_id: str
            - file_name: str
            - page_number: int
            - chunk_id: str

    Returns:
        Number of chunks added.
    """
    if not chunks:
        return 0

    vector_store = _get_vector_store()
    
    texts = [c["text"] for c in chunks]
    metadatas = [
        {
            "file_id": c["file_id"],
            "file_name": c["file_name"],
            "page_number": c["page_number"],
            "chunk_id": c["chunk_id"],
        }
        for c in chunks
    ]
    ids = [c["chunk_id"] for c in chunks]

    logger.info(f"Adding {len(texts)} chunks to Supabase...")
    vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    
    logger.info(f"Successfully added {len(texts)} chunks to Supabase")
    return len(texts)


async def query_similar(query_text: str, top_k: int = 5, file_id: str | None = None) -> list[dict]:
    """
    Query Supabase for similar chunks with optional file filtering.
    """
    supabase_client = get_supabase_client()
    embeddings_model = get_embeddings()

    # Generate query embedding
    logger.info(f"Generating embedding for query: {query_text[:50]}...")
    query_vector = embeddings_model.embed_query(query_text)

    # Call the match_chunks RPC directly
    try:
        res = supabase_client.rpc(
            "match_chunks",
            {
                "query_embedding": query_vector,
                "match_threshold": 0.0,
                "match_count": top_k,
                "filter_file_id": file_id,  # New filter parameter
            }
        ).execute()
        
        results = res.data or []
    except Exception as e:
        logger.error(f"Supabase RPC query failed: {e}")
        raise

    if not results:
        return []

    # Format results
    chunks = []
    for item in results:
        metadata = item.get("metadata", {})
        chunks.append({
            "chunk_id": item.get("id"),
            "text": item.get("content"),
            "file_id": metadata.get("file_id"),
            "file_name": metadata.get("file_name"),
            "page_number": metadata.get("page_number"),
            "distance": 1.0 - (item.get("similarity") or 0),
        })

    logger.info(f"Retrieved {len(chunks)} relevant chunks from Supabase")
    return chunks


async def delete_by_file_id(file_id: str) -> int:
    """
    Delete all chunks belonging to a specific file from Supabase.

    Returns the number of chunks deleted.
    """
    supabase_client = get_supabase_client()
    settings = get_settings()

    try:
        # First, count how many chunks exist for this file
        count_res = (
            supabase_client.table(settings.SUPABASE_VECTOR_TABLE)
            .select("id", count="exact")
            .filter("metadata->>file_id", "eq", file_id)
            .execute()
        )
        count = count_res.count or 0

        if count > 0:
            # Delete by filtering on metadata
            supabase_client.table(settings.SUPABASE_VECTOR_TABLE).delete().filter(
                "metadata->>file_id", "eq", file_id
            ).execute()
            logger.info(f"Deleted {count} chunks for file_id: {file_id} from Supabase")
        else:
            logger.info(f"No chunks found for file_id: {file_id} in Supabase")

        return count
    except Exception as e:
        logger.error(f"Failed to delete chunks for file_id {file_id} from Supabase: {e}")
        raise


def get_stats() -> dict:
    """Get vector store statistics."""
    supabase_client = get_supabase_client()
    settings = get_settings()
    
    res = supabase_client.table(settings.SUPABASE_VECTOR_TABLE).select("id", count="exact").limit(1).execute()
    
    return {
        "total_chunks": res.count or 0,
        "table_name": settings.SUPABASE_VECTOR_TABLE,
    }
