"""
DocMind Backend — FastAPI Application Entry Point.

RAG-based PDF Q&A system with:
- PDF document management (upload, list, delete)
- Intelligent question answering with source attribution
- Custom system prompt support
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import logger
from app.services import vector_store_service
from app.api import documents, query, health, sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Pre-initializes heavy resources on startup for fast first requests.
    """
    logger.info("🧠 DocMind API starting up...")

    # Pre-load embedding model and ChromaDB collection
    vector_store_service.initialize()
    stats = vector_store_service.get_stats()
    logger.info(f"Vector store ready: {stats['total_chunks']} chunks indexed")

    logger.info("✅ DocMind API ready")
    yield

    logger.info("DocMind API shutting down...")


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title="DocMind API",
    description="RAG-based PDF Q&A system with intelligent document management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        settings.FRONTEND_URL.rstrip("/"), # Handle trailing slash
        "http://localhost:5173",
        "http://localhost:3000",
        "https://doc-mind-rag.vercel.app",
        "https://docmind.vercel.app", 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(health.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "DocMind API",
        "version": "1.0.0",
        "docs": "/docs",
    }
