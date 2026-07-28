"""
VoxLens — Process Endpoint

Accepts YouTube URLs or file uploads and kicks off the processing pipeline.
"""

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting
from app.schemas import ProcessURLRequest, MeetingResponse
from app.config import settings

router = APIRouter()


@router.post("/process/url", response_model=MeetingResponse, tags=["Processing"])
async def process_url(request: ProcessURLRequest, db: Session = Depends(get_db)):
    """
    Process a YouTube URL.
    Downloads the video, extracts audio, transcribes, summarizes, and embeds.
    """
    # Validate URL (basic check)
    url = request.url.strip()
    if not any(domain in url for domain in ["youtube.com", "youtu.be"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Please provide a valid YouTube URL.",
        )

    # Create meeting record
    meeting = Meeting(
        source_type="youtube",
        source_url=url,
        language=request.language,
        status="pending",
        progress=0,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    # Dispatch background task
    from app.workers.tasks import process_meeting_task

    process_meeting_task.delay(meeting.id)

    return meeting


@router.post("/process/upload", response_model=MeetingResponse, tags=["Processing"])
async def process_upload(
    file: UploadFile = File(...),
    language: str = Form(default="auto"),
    db: Session = Depends(get_db),
):
    """
    Process an uploaded audio/video file.
    Extracts audio, transcribes, summarizes, and embeds.
    """
    # Validate file type
    allowed_extensions = {
        ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac",
        ".mp4", ".webm", ".mkv", ".avi", ".mov",
    }
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported: {', '.join(sorted(allowed_extensions))}",
        )

    # Check file size
    max_bytes = settings.max_file_size_mb * 1024 * 1024

    # Save uploaded file
    upload_path = settings.upload_path / file.filename
    try:
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            if len(content) > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB.",
                )
            buffer.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create meeting record
    meeting = Meeting(
        source_type="upload",
        file_name=file.filename,
        original_path=str(upload_path),
        language=language,
        status="pending",
        progress=0,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    # Dispatch background task
    from app.workers.tasks import process_meeting_task

    process_meeting_task.delay(meeting.id)

    return meeting
