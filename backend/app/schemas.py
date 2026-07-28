"""
VoxLens — Pydantic Schemas

Request/response schemas for the REST API.
Clean separation between internal ORM models and external API contracts.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# ============================================================
# Request Schemas
# ============================================================


class ProcessURLRequest(BaseModel):
    """Request to process a YouTube URL."""
    url: str = Field(..., description="YouTube video URL")
    language: str = Field(default="auto", description="Language hint: en, hi, auto")


class ChatRequest(BaseModel):
    """Request to chat about a meeting."""
    meeting_id: str = Field(..., description="Meeting ID to query")
    message: str = Field(..., description="User's question")


# ============================================================
# Response Schemas
# ============================================================


class MeetingResponse(BaseModel):
    """Meeting metadata."""
    id: str
    title: str | None
    source_type: str
    source_url: str | None
    file_name: str | None
    language: str
    status: str
    error_message: str | None
    progress: int
    duration_seconds: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MeetingListResponse(BaseModel):
    """List of meetings."""
    meetings: list[MeetingResponse]
    total: int


class TranscriptChunkResponse(BaseModel):
    """A single transcript segment."""
    id: str
    chunk_index: int
    start_time: float
    end_time: float
    text: str

    model_config = {"from_attributes": True}


class TranscriptResponse(BaseModel):
    """Full transcript for a meeting."""
    meeting_id: str
    chunks: list[TranscriptChunkResponse]
    full_text: str


class ActionItemResponse(BaseModel):
    """An extracted action item."""
    task: str
    owner: str = "Unknown"
    deadline: str = "Not specified"


class SummaryReportResponse(BaseModel):
    """Generated meeting intelligence report."""
    meeting_id: str
    summary: str | None
    bullet_points: list[str] | None
    key_takeaways: list[str] | None
    action_items: list[ActionItemResponse] | None
    decisions: list[str] | None
    open_questions: list[str] | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    """A single chat message."""
    id: str
    role: str
    content: str
    sources: list[dict] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    message: ChatMessageResponse
    sources: list[dict] | None = None


class JobStatusResponse(BaseModel):
    """Job processing status."""
    meeting_id: str
    status: str
    progress: int
    error_message: str | None = None


class HealthResponse(BaseModel):
    """API health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    service: str = "VoxLens API"


class ExportResponse(BaseModel):
    """Markdown export of meeting data."""
    meeting_id: str
    markdown: str
    filename: str
