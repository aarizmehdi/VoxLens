"""
VoxLens — Audio Utilities

FFmpeg helper functions for audio extraction, normalization, and chunking.
All audio is converted to mono 16kHz WAV for transcription compatibility.
"""

import subprocess
import logging
from pathlib import Path

logger = logging.getLogger("voxlens.audio")


def get_audio_duration(audio_path: Path) -> float:
    """Get the duration of an audio file in seconds using FFprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        import json
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        logger.warning(f"Could not get audio duration: {e}")
        return 0.0


def extract_audio_from_video(video_path: Path, output_path: Path) -> Path:
    """
    Extract audio track from a video file.
    Output: mono 16kHz WAV.
    """
    logger.info(f"Extracting audio from {video_path.name}")

    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",                  # No video
        "-acodec", "pcm_s16le", # 16-bit PCM
        "-ar", "16000",         # 16kHz sample rate
        "-ac", "1",             # Mono
        "-y",                   # Overwrite output
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr}")

    logger.info(f"Audio extracted: {output_path.name}")
    return output_path


def normalize_audio(input_path: Path, output_path: Path) -> Path:
    """
    Normalize audio to mono 16kHz WAV with volume normalization.
    Suitable for Whisper transcription.
    """
    logger.info(f"Normalizing audio: {input_path.name}")

    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",  # EBU R128 loudness normalization
        "-y",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg normalization failed: {result.stderr}")

    logger.info(f"Audio normalized: {output_path.name}")
    return output_path


def chunk_audio(
    audio_path: Path,
    output_dir: Path,
    chunk_duration: int = 300,
) -> list[Path]:
    """
    Split a long audio file into chunks of specified duration (seconds).
    Returns list of chunk file paths.
    """
    duration = get_audio_duration(audio_path)
    if duration <= 0:
        logger.warning("Could not determine duration, returning single file")
        return [audio_path]

    if duration <= chunk_duration:
        logger.info(f"Audio is {duration:.0f}s — no chunking needed")
        return [audio_path]

    output_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    chunk_index = 0
    start_time = 0.0

    while start_time < duration:
        chunk_path = output_dir / f"chunk_{chunk_index:04d}.wav"
        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-ss", str(start_time),
            "-t", str(chunk_duration),
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            str(chunk_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Chunking failed at {start_time}s: {result.stderr}")
            break

        chunks.append(chunk_path)
        chunk_index += 1
        start_time += chunk_duration

    logger.info(f"Audio split into {len(chunks)} chunks")
    return chunks


def is_video_file(file_path: Path) -> bool:
    """Check if a file is a video format (needs audio extraction)."""
    video_extensions = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".flv", ".wmv"}
    return file_path.suffix.lower() in video_extensions


def is_audio_file(file_path: Path) -> bool:
    """Check if a file is already an audio format."""
    audio_extensions = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".wma"}
    return file_path.suffix.lower() in audio_extensions
