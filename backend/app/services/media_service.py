"""
VoxLens — Media Service

Handles YouTube downloading and file processing.
Uses yt-dlp for YouTube and FFmpeg for audio extraction/normalization.
"""

import logging
from pathlib import Path

import yt_dlp

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
    Download audio from a YouTube video using yt-dlp.

    Returns:
        dict with keys: audio_path, title, duration
    """
    output_dir = settings.media_path / meeting_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "postprocessor_args": [
            "-ar", "16000",
            "-ac", "1",
        ],
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }

    logger.info(f"Downloading YouTube audio: {url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Untitled")
        duration = info.get("duration", 0)

    # Find the downloaded WAV file
    wav_files = list(output_dir.glob("*.wav"))
    if not wav_files:
        raise RuntimeError("YouTube audio download failed — no WAV file produced")

    audio_path = wav_files[0]
    logger.info(f"YouTube download complete: {audio_path.name} ({duration}s)")

    return {
        "audio_path": audio_path,
        "title": title,
        "duration": float(duration) if duration else get_audio_duration(audio_path),
    }


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
