"""
API routes for managing chat sessions.
"""

from fastapi import APIRouter, HTTPException, status
from app.services import session_service
from app.core.logging import logger

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_new_session(title: str = "New Conversation"):
    try:
        return session_service.create_session(title)
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def list_sessions():
    return session_service.get_sessions()

@router.get("/{session_id}/messages")
async def get_messages(session_id: str):
    return session_service.get_session_messages(session_id)

@router.delete("/{session_id}")
async def remove_session(session_id: str):
    session_service.delete_session(session_id)
    return {"message": "Session deleted"}
