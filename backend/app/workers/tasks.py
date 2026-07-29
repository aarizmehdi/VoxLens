"""
VoxLens — Background Tasks

The main processing pipeline that orchestrates:
1. Media download/extraction
2. Audio normalization
3. Transcription
4. Summarization & extraction
5. Embedding for RAG

Each step updates the meeting record with progress information.
"""

import logging
from pathlib import Path


from app.database import SessionLocal
from app.models import Meeting, TranscriptChunk, SummaryReport
from app.config import settings

logger = logging.getLogger("voxlens.tasks")


def _update_meeting_status(
    meeting_id: str,
    status: str,
    progress: int,
    error: str | None = None,
    **kwargs,
):
    """Update meeting status in the database."""
    db = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = status
            meeting.progress = progress
            meeting.error_message = error
            for key, value in kwargs.items():
                if hasattr(meeting, key):
                    setattr(meeting, key, value)
            db.commit()
    finally:
        db.close()


def process_meeting_task(meeting_id: str):
    """
    Main processing pipeline for a meeting.
    Handles the full flow from media ingestion to RAG embedding.
    """
    logger.info(f"Starting processing pipeline for meeting: {meeting_id}")

    db = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            logger.error(f"Meeting {meeting_id} not found")
            return

        source_type = meeting.source_type
        source_url = meeting.source_url
        original_path = meeting.original_path
        language = meeting.language
    finally:
        db.close()

    try:
        # ============================================================
        # Step 1: Download / Prepare Media
        # ============================================================
        _update_meeting_status(meeting_id, "downloading", 10)
        logger.info("Step 1: Media acquisition")

        from app.services.media_service import process_uploaded_file

        media_result = process_uploaded_file(Path(original_path), meeting_id)
        audio_path = media_result["audio_path"]
        duration = media_result.get("duration")
        
        _update_meeting_status(
            meeting_id, "processing_audio", 20,
            duration_seconds=duration,
            audio_path=str(audio_path),
        )

        # ============================================================
        # Step 2: Prepare Audio Chunks
        # ============================================================
        _update_meeting_status(meeting_id, "processing_audio", 30)
        logger.info("Step 2: Audio chunking")

        from app.services.media_service import prepare_audio_chunks

        audio_chunks = prepare_audio_chunks(audio_path, meeting_id)
        logger.info(f"Audio prepared: {len(audio_chunks)} chunk(s)")

        # ============================================================
        # Step 3: Transcription
        # ============================================================
        _update_meeting_status(meeting_id, "transcribing", 40)
        logger.info("Step 3: Transcription")

        from app.services.transcription_service import transcribe

        all_segments = []
        time_offset = 0.0
        chunk_duration = settings.audio_chunk_duration_seconds

        for i, chunk_path in enumerate(audio_chunks):
            progress = 40 + int((i / max(len(audio_chunks), 1)) * 20)
            _update_meeting_status(meeting_id, "transcribing", progress)

            result = transcribe(chunk_path, language=language)

            for seg in result.segments:
                all_segments.append({
                    "start": seg.start + time_offset,
                    "end": seg.end + time_offset,
                    "text": seg.text,
                })

            time_offset += chunk_duration

            # Update language if auto-detected
            if language == "auto" and result.language:
                language = result.language

        # Save transcript chunks to database
        db = SessionLocal()
        try:
            for i, seg in enumerate(all_segments):
                chunk = TranscriptChunk(
                    meeting_id=meeting_id,
                    chunk_index=i,
                    start_time=seg["start"],
                    end_time=seg["end"],
                    text=seg["text"],
                )
                db.add(chunk)
            db.commit()

            # Update meeting language
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                meeting.language = language
                db.commit()
        finally:
            db.close()

        full_transcript = " ".join(seg["text"] for seg in all_segments)
        logger.info(
            f"Transcription complete: {len(all_segments)} segments, "
            f"{len(full_transcript)} chars"
        )

        # ============================================================
        # Step 4: Summarization & Extraction
        # ============================================================
        _update_meeting_status(meeting_id, "summarizing", 65)
        logger.info("Step 4: Summarization & extraction")

        from app.services.summarization_service import generate_full_report

        report = generate_full_report(full_transcript)

        # Save report to database
        db = SessionLocal()
        try:
            summary_report = SummaryReport(
                meeting_id=meeting_id,
                summary=report.summary,
                bullet_points=report.bullet_points,
                key_takeaways=report.key_takeaways,
                action_items=report.action_items,
                decisions=report.decisions,
                open_questions=report.open_questions,
            )
            db.add(summary_report)

            # Update meeting title if generated
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting and report.title:
                meeting.title = report.title
            db.commit()
        finally:
            db.close()

        logger.info("Report saved to database")

        # ============================================================
        # Step 5: Embedding for RAG
        # ============================================================
        _update_meeting_status(meeting_id, "embedding", 85)
        logger.info("Step 5: Embedding transcript for RAG")

        from app.services.embedding_service import chunk_transcript, embed_and_store

        text_chunks = chunk_transcript(full_transcript)
        embed_and_store(meeting_id, text_chunks)

        logger.info("Embeddings stored in ChromaDB")

        # ============================================================
        # Complete!
        # ============================================================
        _update_meeting_status(meeting_id, "completed", 100)
        logger.info(f"✅ Meeting {meeting_id} processed successfully!")

    except Exception as e:
        logger.error(f"❌ Processing failed for meeting {meeting_id}: {e}", exc_info=True)
        _update_meeting_status(meeting_id, "failed", 0, error=str(e))
        raise
