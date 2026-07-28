"""
VoxLens — Text Utilities

Text cleaning, chunking, and formatting helpers.
"""

import re
import logging

logger = logging.getLogger("voxlens.text")


def clean_transcript_text(text: str) -> str:
    """Clean raw transcript text for better readability."""
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove repeated phrases (common Whisper hallucination)
    text = re.sub(r"(.{20,}?)\1{2,}", r"\1", text)
    return text


def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def estimate_language(text: str) -> str:
    """
    Simple heuristic to detect if text is primarily Hindi/Devanagari or English.
    Returns 'hi' for Hindi/Hinglish, 'en' for English.
    """
    if not text:
        return "en"

    # Count Devanagari characters
    devanagari_count = len(re.findall(r"[\u0900-\u097F]", text))
    total_alpha = len(re.findall(r"[a-zA-Z\u0900-\u097F]", text))

    if total_alpha == 0:
        return "en"

    devanagari_ratio = devanagari_count / total_alpha
    if devanagari_ratio > 0.3:
        return "hi"
    return "en"


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length, preserving word boundaries."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length].rsplit(" ", 1)[0]
    return truncated + "..."


def combine_transcript_segments(
    segments: list[dict],
) -> str:
    """Combine transcript segments into a single text string."""
    return " ".join(seg.get("text", "").strip() for seg in segments if seg.get("text"))
