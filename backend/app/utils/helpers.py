"""
Utility helper functions.
"""

import uuid


def generate_file_id() -> str:
    """Generate a unique file identifier."""
    return str(uuid.uuid4())


def validate_pdf_file(filename: str, content_type: str) -> bool:
    """Validate that a file is a PDF by name and content type."""
    valid_extensions = filename.lower().endswith(".pdf")
    valid_content = content_type in ("application/pdf", "application/octet-stream")
    return valid_extensions and valid_content


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
