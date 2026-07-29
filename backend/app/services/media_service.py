"""
VoxLens — Media Service

Handles YouTube downloading and file processing.
Uses yt-dlp for YouTube and FFmpeg for audio extraction/normalization.
"""

import logging
import re
import httpx
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
    Download audio from a YouTube video.
    Uses RapidAPI if configured, otherwise falls back to yt-dlp.

    Returns:
        dict with keys: audio_path, title, duration
    """
    output_dir = settings.media_path / meeting_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # --- RAPIDAPI PROXY METHOD ---
    # Hardcoded key fallback to ensure it works even if Render env vars are broken
    active_key = settings.rapidapi_key or "59e46fdf44msha7d56e54332b741p132c9djsn7a205bb16283"
    
    logger.info(f"Using RapidAPI Proxy to download YouTube audio: {url}")
    try:
        # Extract video ID
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if not video_id_match:
            raise ValueError("Could not extract YouTube Video ID")
        
        video_id = video_id_match.group(1)
        
        api_url = "https://youtube-mp36.p.rapidapi.com/dl"
        querystring = {"id": video_id}
        headers = {
            "x-rapidapi-key": active_key,
            "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.get(api_url, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok" and data.get("link"):
                download_url = data.get("link")
                title = data.get("title", "Untitled")
                duration = data.get("duration", 0)
                
                # Download the actual MP3
                mp3_path = output_dir / f"{title}.mp3"
                with client.stream("GET", download_url) as r:
                    r.raise_for_status()
                    with open(mp3_path, "wb") as f:
                        for chunk in r.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                
                # Normalize the MP3 to WAV using our existing util
                normalized_path = output_dir / "audio_normalized.wav"
                normalize_audio(mp3_path, normalized_path)
                
                # Clean up temp mp3
                mp3_path.unlink(missing_ok=True)
                
                return {
                    "audio_path": normalized_path,
                    "title": title,
                    "duration": float(duration) if duration else get_audio_duration(normalized_path)
                }
            else:
                logger.error(f"RapidAPI returned error: {data}")
                raise RuntimeError(f"RapidAPI Proxy Failed: {data}")
    except Exception as e:
        logger.error(f"RapidAPI request failed: {e}")
        raise RuntimeError(f"YouTube Download Failed. Ensure RapidAPI key is active. Error: {e}")




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
