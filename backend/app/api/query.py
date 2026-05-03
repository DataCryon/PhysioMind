"""
Query API route.
Handles RAG-based question answering with source attribution.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.query import QueryRequest, QueryResponse
from app.rag.generation.rag_graph import run_rag_pipeline
from app.services import session_service
from app.core.logging import logger

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question against uploaded PDF documents.

    Uses the LangGraph RAG pipeline:
    1. Retrieve relevant chunks from ChromaDB
    2. Generate answer using Groq LLM
    3. Format source attributions from metadata
    """
    try:
        session_id = request.session_id
        history = request.history
        
        # If session_id is provided, fetch last 3 messages from database to use as context
        if session_id:
            db_messages = session_service.get_session_messages(session_id, limit=3)
            # Format DB messages for the RAG pipeline
            db_history = [{"role": m["role"], "content": m["content"]} for m in db_messages]
            # Use DB history if request history is empty (useful for direct session loads)
            if not history:
                history = db_history

        logger.info(
            f"Query received: {request.question[:80]}... "
            f"(session: {session_id}, history: {len(history)} msgs)"
        )

        result = await run_rag_pipeline(
            question=request.question,
            history=history,
            file_id=request.file_id,
            system_prompt=request.system_prompt,
        )

        # Store interaction in database if session_id exists
        if session_id:
            try:
                session_service.add_message(session_id, "user", request.question)
                session_service.add_message(session_id, "assistant", result["answer"])
            except Exception as db_err:
                logger.error(f"Failed to store chat history: {db_err}")

        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            chunks_used=result["chunks_used"],
        )

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}",
        )
