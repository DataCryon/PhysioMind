from __future__ import annotations
"""
LangGraph-based RAG pipeline.
Orchestrates retrieval → generation → source formatting as a stateful graph.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

from app.rag.retrieval.retriever import retrieve_relevant_chunks
from app.rag.generation.generator import generate_answer
from app.schemas.query import SourceInfo
from app.core.logging import logger


class RAGState(TypedDict):
    """State passed between graph nodes."""

    question: str
    history: list[dict]
    file_id: str | None
    system_prompt: str | None
    context_chunks: list[dict]
    answer: str
    sources: list[dict]


# --- Graph Nodes ---

async def retrieve_node(state: RAGState) -> dict:
    """Node 1: Retrieve relevant chunks from the vector store."""
    question = state["question"]
    file_id = state.get("file_id")
    logger.info(f"[RAG Graph] Retrieve node — query: {question[:60]}... (filter: {file_id})")

    chunks = await retrieve_relevant_chunks(question, file_id=file_id)

    return {"context_chunks": chunks}


async def generate_node(state: RAGState) -> dict:
    """Node 2: Generate answer using LLM with retrieved context and history."""
    question = state["question"]
    history = state.get("history", [])
    context_chunks = state["context_chunks"]
    system_prompt = state.get("system_prompt")

    logger.info(f"[RAG Graph] Generate node — {len(context_chunks)} chunks, {len(history)} messages history")

    if not context_chunks and not history:
        return {
            "answer": (
                "I don't have any relevant information from the uploaded documents "
                "to answer this question. Please make sure you've uploaded relevant "
                "PDF documents and try again."
            )
        }

    # Pass history to generator for conversation feel
    answer = await generate_answer(question, context_chunks, system_prompt, history=history)
    return {"answer": answer}


async def format_sources_node(state: RAGState) -> dict:
    """Node 3: Extract unique source attributions from chunk metadata."""
    context_chunks = state["context_chunks"]

    # Deduplicate sources by (file_name, page_number)
    seen = set()
    sources = []

    for chunk in context_chunks:
        key = (chunk["file_name"], chunk["page_number"])
        if key not in seen:
            seen.add(key)
            sources.append({
                "file_name": chunk["file_name"],
                "page_number": chunk["page_number"],
                "chunk_id": chunk.get("chunk_id", ""),
                "relevance_score": round(1 - chunk.get("distance", 0), 4),
            })

    # Sort by relevance (highest first)
    sources.sort(key=lambda s: s["relevance_score"], reverse=True)

    logger.info(f"[RAG Graph] Source format node — {len(sources)} unique sources")
    return {"sources": sources}


# --- Build the Graph ---

def _build_rag_graph() -> StateGraph:
    """Construct the LangGraph RAG pipeline."""
    graph = StateGraph(RAGState)

    # Add nodes
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("format_sources", format_sources_node)

    # Define edges: retrieve → generate → format_sources → END
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "format_sources")
    graph.add_edge("format_sources", END)

    return graph


# Compile graph once at module level
_compiled_graph = _build_rag_graph().compile()


async def run_rag_pipeline(
    question: str, 
    history: list[dict] = [], 
    file_id: str | None = None,
    system_prompt: str | None = None
) -> dict:
    """
    Execute the full RAG pipeline.

    Args:
        question: User's question.
        history: Chat history.
        file_id: Optional PDF filter.
        system_prompt: Optional custom system instruction.

    Returns:
        Dict with 'answer' (str), 'sources' (list[SourceInfo]), 'chunks_used' (int).
    """
    logger.info(f"[RAG Pipeline] Starting for question: {question[:80]}...")

    initial_state: RAGState = {
        "question": question,
        "history": history,
        "file_id": file_id,
        "system_prompt": system_prompt,
        "context_chunks": [],
        "answer": "",
        "sources": [],
    }

    # Run the graph
    result = await _compiled_graph.ainvoke(initial_state)

    # Build response
    sources = [
        SourceInfo(
            file_name=s["file_name"],
            page_number=s["page_number"],
            chunk_id=s.get("chunk_id", ""),
            relevance_score=s.get("relevance_score", 0.0),
        )
        for s in result.get("sources", [])
    ]

    logger.info(
        f"[RAG Pipeline] Complete — answer length: {len(result.get('answer', ''))}, "
        f"sources: {len(sources)}"
    )

    return {
        "answer": result.get("answer", ""),
        "sources": sources,
        "chunks_used": len(result.get("context_chunks", [])),
    }
