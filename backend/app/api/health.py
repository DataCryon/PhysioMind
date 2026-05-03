"""
Health check API endpoint.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint for monitoring and deployment readiness."""
    return {
        "status": "healthy",
        "service": "PhysioMind API",
        "version": "1.0.0",
    }
