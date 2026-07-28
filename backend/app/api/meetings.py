"""
VoxLens — Meetings Endpoint

List and retrieve meeting records.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Meeting
from app.schemas import MeetingResponse, MeetingListResponse

router = APIRouter()


@router.get("/meetings", response_model=MeetingListResponse, tags=["Meetings"])
async def list_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all meetings, most recent first."""
    total = db.query(Meeting).count()
    meetings = (
        db.query(Meeting)
        .order_by(desc(Meeting.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return MeetingListResponse(
        meetings=[MeetingResponse.model_validate(m) for m in meetings],
        total=total,
    )


@router.get(
    "/meetings/{meeting_id}",
    response_model=MeetingResponse,
    tags=["Meetings"],
)
async def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    """Get a specific meeting by ID."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.delete("/meetings/{meeting_id}", tags=["Meetings"])
async def delete_meeting(meeting_id: str, db: Session = Depends(get_db)):
    """Delete a meeting and all associated data."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    db.delete(meeting)
    db.commit()

    return {"detail": "Meeting deleted successfully"}
