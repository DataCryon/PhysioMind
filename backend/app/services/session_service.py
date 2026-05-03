"""
Service for managing persistent chat sessions and messages in Supabase.
"""

from typing import Optional
from app.services.supabase_service import get_supabase_client
from app.core.logging import logger

def create_session(title: str = "New Conversation") -> dict:
    """Create a new chat session."""
    supabase = get_supabase_client()
    
    # Optional: Trigger cleanup of old sessions (simple retention policy)
    try:
        supabase.rpc("cleanup_old_sessions", {}).execute()
    except Exception:
        pass # Ignore if function doesn't exist yet
        
    res = supabase.table("chat_sessions").insert({"title": title}).execute()
    return res.data[0]

def get_sessions(limit: int = 20) -> list[dict]:
    """Fetch recent chat sessions."""
    supabase = get_supabase_client()
    res = supabase.table("chat_sessions").select("*").order("created_at", desc=True).limit(limit).execute()
    return res.data or []

def get_session_messages(session_id: str, limit: int = 50) -> list[dict]:
    """Fetch messages for a specific session."""
    supabase = get_supabase_client()
    res = supabase.table("chat_messages").select("*").eq("session_id", session_id).order("created_at", desc=False).limit(limit).execute()
    return res.data or []

def add_message(session_id: str, role: str, content: str) -> dict:
    """Add a message to a session."""
    supabase = get_supabase_client()
    res = supabase.table("chat_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()
    
    # Update session title if it's the first user message
    if role == "user":
        try:
            messages = get_session_messages(session_id, limit=2)
            if len(messages) == 1: # This was the first message
                title = content[:30] + "..." if len(content) > 30 else content
                supabase.table("chat_sessions").update({"title": title}).eq("id", session_id).execute()
        except Exception:
            pass

    return res.data[0]

def delete_session(session_id: str) -> bool:
    """Delete a chat session and its messages."""
    supabase = get_supabase_client()
    supabase.table("chat_sessions").delete().eq("id", session_id).execute()
    return True
