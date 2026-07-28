"""
VoxLens — Health Check Endpoint
"""

from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check if the API is running and healthy."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        service="VoxLens API",
    )
