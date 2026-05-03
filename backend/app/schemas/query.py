"""
Pydantic schemas for query-related API requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for asking a question."""

    question: str = Field(..., min_length=1, max_length=2000, description="The question to ask")
    session_id: Optional[str] = Field(None, description="Optional chat session ID for persistence")
    history: list[dict] = Field(default_factory=list, description="Previous messages for context")
    file_id: Optional[str] = Field(None, description="Optional ID of a specific PDF to search within")
    system_prompt: Optional[str] = Field(
        None,
        max_length=5000,
        description="Optional custom instruction to influence the AI's response style",
    )


class SourceInfo(BaseModel):
    """Information about a source chunk used in the answer."""

    file_name: str
    page_number: int
    chunk_id: str = ""
    relevance_score: float = 0.0


class QueryResponse(BaseModel):
    """Response schema for a query answer."""

    answer: str
    sources: list[SourceInfo]
    chunks_used: int = 0
