"""
VoxLens — Media Service

Handles YouTube downloading and file processing.
Uses yt-dlp for YouTube and FFmpeg for audio extraction/normalization.
"""

import logging
import re
import logging
from pathlib import Path
from pytubefix import YouTube

from app.config import settings
from app.utils.audio import (
    extract_audio_from_video,
    normalize_audio,
    chunk_audio,
    is_video_file,
    get_audio_duration,
)

logger = logging.getLogger("voxlens.media")


def download_youtube_audio(url: str, meeting_id: str) -> dict:
    """
    Download audio from a YouTube video using pytubefix (natively bypasses bot blocks).
    """
    output_dir = settings.media_path / meeting_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading YouTube audio using pytubefix: {url}")
    
    try:
        # Create YouTube object (automatically spoof clients and generates po_token to bypass bot blocks)
        yt = YouTube(url)
        
        title = yt.title or "Untitled"
        duration = yt.length or 0
        
        # Get highest quality audio stream
        ys = yt.streams.get_audio_only()
        if not ys:
            raise RuntimeError("No audio streams found for this video")
            
        # Download as m4a
        m4a_path = output_dir / "raw_audio.m4a"
        ys.download(output_path=str(output_dir), filename="raw_audio.m4a")
        
        if not m4a_path.exists():
            raise RuntimeError("YouTube audio download failed — file not written to disk")
            
        # Normalize to WAV using our existing ffmpeg utility
        normalized_path = output_dir / "audio_normalized.wav"
        normalize_audio(m4a_path, normalized_path)
        
        # Clean up raw m4a
        m4a_path.unlink(missing_ok=True)
        
        actual_duration = float(duration) if duration else get_audio_duration(normalized_path)
        logger.info(f"YouTube download complete: {normalized_path.name} ({actual_duration}s)")
        
        return {
            "audio_path": normalized_path,
            "title": title,
            "duration": actual_duration,
        }
    except Exception as e:
        logger.error(f"pytubefix failed to download {url}: {e}")
        raise RuntimeError(f"YouTube Download Failed. Error: {e}")




def process_uploaded_file(file_path: Path, meeting_id: str) -> dict:
    """
    Process an uploaded audio or video file.
    Extracts audio if video, normalizes to 16kHz mono WAV.

    Returns:
        dict with keys: audio_path, duration
    """
    output_dir = settings.media_path / meeting_id
    output_dir.mkdir(parents=True, exist_ok=True)

    normalized_path = output_dir / "audio_normalized.wav"

    if is_video_file(file_path):
        # Extract audio from video first
        raw_audio = output_dir / "audio_raw.wav"
        extract_audio_from_video(file_path, raw_audio)
        normalize_audio(raw_audio, normalized_path)
        # Clean up raw audio
        raw_audio.unlink(missing_ok=True)
    else:
        # Already audio — just normalize
        normalize_audio(file_path, normalized_path)

    duration = get_audio_duration(normalized_path)
    logger.info(f"Upload processed: {normalized_path.name} ({duration:.0f}s)")

    return {
        "audio_path": normalized_path,
        "duration": duration,
    }


def prepare_audio_chunks(
    audio_path: Path,
    meeting_id: str,
    chunk_duration: int | None = None,
) -> list[Path]:
    """
    Split audio into chunks for transcription.
    Returns list of chunk file paths.
    """
    if chunk_duration is None:
        chunk_duration = settings.audio_chunk_duration_seconds

    chunks_dir = settings.media_path / meeting_id / "chunks"
    return chunk_audio(audio_path, chunks_dir, chunk_duration)
