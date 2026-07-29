"""
VoxLens — FastAPI Application

Main application factory with CORS, lifespan events, and route mounting.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.router import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("voxlens")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 VoxLens API starting up...")

    # Initialize database tables
    init_db()
    logger.info("✅ Database initialized")

    # Ensure directories exist
    settings.upload_path
    settings.media_path
    settings.chroma_path
    logger.info("✅ Storage directories ready")

    yield

    logger.info("👋 VoxLens API shutting down...")


app = FastAPI(
    title="VoxLens API",
    description="AI Meeting & Video Assistant — Transcription, Summarization, and RAG Chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
allow_all = "*" in settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else settings.cors_origins_list,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — API information."""
    return {
        "name": "VoxLens API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
