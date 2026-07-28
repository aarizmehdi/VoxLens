"""
VoxLens — Job Status Endpoint

Allows the frontend to poll for processing progress.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting
from app.schemas import JobStatusResponse

router = APIRouter()


@router.get(
    "/jobs/{meeting_id}",
    response_model=JobStatusResponse,
    tags=["Jobs"],
)
async def get_job_status(meeting_id: str, db: Session = Depends(get_db)):
    """Get the processing status of a meeting job."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        meeting_id=meeting.id,
        status=meeting.status,
        progress=meeting.progress,
        error_message=meeting.error_message,
    )
