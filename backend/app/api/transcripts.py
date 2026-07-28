"""
VoxLens — Transcript Endpoint

Retrieve transcript data for a meeting.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting, TranscriptChunk
from app.schemas import TranscriptResponse, TranscriptChunkResponse

router = APIRouter()


@router.get(
    "/transcripts/{meeting_id}",
    response_model=TranscriptResponse,
    tags=["Transcripts"],
)
async def get_transcript(meeting_id: str, db: Session = Depends(get_db)):
    """Get the full transcript for a meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    chunks = (
        db.query(TranscriptChunk)
        .filter(TranscriptChunk.meeting_id == meeting_id)
        .order_by(TranscriptChunk.chunk_index)
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="Transcript not yet available. The meeting may still be processing.",
        )

    full_text = " ".join(chunk.text for chunk in chunks)

    return TranscriptResponse(
        meeting_id=meeting_id,
        chunks=[TranscriptChunkResponse.model_validate(c) for c in chunks],
        full_text=full_text,
    )
