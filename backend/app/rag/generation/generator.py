from __future__ import annotations
"""
LLM answer generation module.
Uses Groq API via LangChain for fast inference.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.core.config import get_settings
from app.core.logging import logger

# Lazy-initialized LLM instance
_llm: ChatGroq | None = None

DEFAULT_SYSTEM_PROMPT = """You are PhysioMind, an intelligent document assistant. 
Your role is to answer questions accurately based ONLY on the provided context from uploaded PDF documents.

Rules:
- Answer based strictly on the provided context. Do not make up information.
- If the context doesn't contain enough information to answer, say so clearly.
- Be concise but thorough in your answers.
- Use clear, professional language.
- If the question is ambiguous, interpret it in the most reasonable way given the context.
- Format your response with proper structure when appropriate (bullet points, numbered lists, etc.)."""


def _get_llm() -> ChatGroq:
    """Get or create the Groq LLM instance."""
    global _llm
    if _llm is None:
        settings = get_settings()
        _llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.LLM_MODEL,
            temperature=0.1,  # Low temperature for factual responses
            max_tokens=2048,
        )
        logger.info(f"Groq LLM initialized: {settings.LLM_MODEL}")
    return _llm


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context string for the LLM."""
    if not chunks:
        return "No relevant context found."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['file_name']}, Page {chunk['page_number']}]\n"
            f"{chunk['text']}"
        )

    return "\n\n---\n\n".join(context_parts)


async def generate_answer(
    query: str,
    context_chunks: list[dict],
    system_prompt: str | None = None,
    history: list[dict] = [],
) -> str:
    """
    Generate an answer using the Groq LLM with retrieved context and chat history.
    """
    llm = _get_llm()

    # Build system message
    base_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
    full_system = (
        f"{base_prompt}\n\n"
        "When answering, reference the source documents naturally. "
        "The sources are provided in the context below."
    )

    # Format context from chunks
    context_text = format_context(context_chunks)

    # Build messages list
    messages = [SystemMessage(content=full_system)]

    # Add chat history (limited to last 4 messages to save context space)
    # History format: {"role": "user"|"assistant", "content": "text"}
    for msg in history[-4:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    # Build current user message with context
    user_message = (
        f"Context from uploaded documents:\n\n{context_text}\n\n"
        f"---\n\n"
        f"Question: {query}\n\n"
        f"Please answer based on the context above."
    )
    messages.append(HumanMessage(content=user_message))

    logger.info(f"Generating answer with {len(history)} history msgs for query: {query[:80]}...")

    response = await llm.ainvoke(messages)

    logger.info(f"Answer generated ({len(response.content)} chars)")
    return response.content
