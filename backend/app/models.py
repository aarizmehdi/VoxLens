"""
VoxLens — ORM Models

SQLAlchemy models for the core data entities:
- Meeting: top-level record for a processed video/audio
- TranscriptChunk: individual segments of the transcript
- SummaryReport: generated meeting intelligence
- ChatMessage: conversation history for RAG chat
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Meeting(Base):
    """A processed meeting/video/audio recording."""

    __tablename__ = "meetings"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=True)
    source_type = Column(String, nullable=False)  # "youtube" | "upload"
    source_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    language = Column(String, default="en")
    status = Column(String, default="pending")
    # Status values: pending, downloading, processing_audio, transcribing,
    #                summarizing, embedding, completed, failed
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Audio file paths
    audio_path = Column(String, nullable=True)
    original_path = Column(String, nullable=True)

    # Relationships
    transcript_chunks = relationship(
        "TranscriptChunk",
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="TranscriptChunk.chunk_index",
    )
    summary_report = relationship(
        "SummaryReport",
        back_populates="meeting",
        uselist=False,
        cascade="all, delete-orphan",
    )
    chat_messages = relationship(
        "ChatMessage",
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class TranscriptChunk(Base):
    """A segment of the meeting transcript with timing data."""

    __tablename__ = "transcript_chunks"

    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)  # seconds
    end_time = Column(Float, nullable=False)  # seconds
    text = Column(Text, nullable=False)
    embedding_id = Column(String, nullable=True)

    meeting = relationship("Meeting", back_populates="transcript_chunks")


class SummaryReport(Base):
    """Generated meeting intelligence: summary, action items, decisions."""

    __tablename__ = "summary_reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False, unique=True)
    summary = Column(Text, nullable=True)
    bullet_points = Column(JSON, nullable=True)  # list[str]
    key_takeaways = Column(JSON, nullable=True)  # list[str]
    action_items = Column(JSON, nullable=True)  # list[{owner, deadline, task}]
    decisions = Column(JSON, nullable=True)  # list[str]
    open_questions = Column(JSON, nullable=True)  # list[str]
    created_at = Column(DateTime, default=utcnow)

    meeting = relationship("Meeting", back_populates="summary_report")


class ChatMessage(Base):
    """A message in the RAG chat conversation."""

    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # list of source chunk references
    created_at = Column(DateTime, default=utcnow)

    meeting = relationship("Meeting", back_populates="chat_messages")
