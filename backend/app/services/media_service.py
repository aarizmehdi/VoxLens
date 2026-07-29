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
    if settings.rapidapi_key:
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
                "x-rapidapi-key": settings.rapidapi_key,
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
                    logger.info("Falling back to yt-dlp...")
        except Exception as e:
            logger.error(f"RapidAPI request failed: {e}")
            logger.info("Falling back to yt-dlp...")

    # --- YT-DLP FALLBACK METHOD ---
    logger.info(f"Downloading YouTube audio using yt-dlp: {url}")
    
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
        "extractor_args": {
            "youtube": {
                "player_client": ["ios", "android"]
            }
        },
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }

    # Check for Render Secret File first (Docker uses /etc/secrets)
    render_cookies = Path("/etc/secrets/youtube_cookies.txt")
    local_cookies = Path("youtube_cookies.txt")
    
    if render_cookies.exists():
        ydl_opts["cookiefile"] = str(render_cookies.absolute())
        logger.info("Injecting authenticated YouTube cookies from Render Secret File")
    elif local_cookies.exists():
        ydl_opts["cookiefile"] = str(local_cookies.absolute())
        logger.info(f"Injecting authenticated YouTube cookies from {local_cookies.absolute()}")

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
