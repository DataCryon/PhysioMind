"""
Document data model for internal representation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Document:
    """Internal representation of an uploaded PDF document."""

    id: str
    file_name: str
    file_size: int
    page_count: int = 0
    chunk_count: int = 0
    supabase_path: str = ""
    created_at: Optional[datetime] = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "page_count": self.page_count,
            "chunk_count": self.chunk_count,
            "supabase_path": self.supabase_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
