"""
VoxLens — Transcription Service

Routes transcription to the appropriate- Whisper / Faster Whisper (Local, robust, multi-language)
"""

import logging
import httpx
from pathlib import Path
from dataclasses import dataclass, field

from app.config import settings
from app.utils.text import clean_transcript_text, estimate_language

logger = logging.getLogger("voxlens.transcription")


@dataclass
class TranscriptSegment:
    """A single segment of transcribed audio."""
    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    """Complete transcription result."""
    segments: list[TranscriptSegment] = field(default_factory=list)
    full_text: str = ""
    language: str = "en"
    engine: str = "whisper"


# Cache the Whisper model to avoid reloading
_whisper_model = None


def _get_whisper_model():
    """Lazy-load the faster-whisper model."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel

        model_size = settings.whisper_model_size
        logger.info(f"Loading Whisper model: {model_size}")

        # Use CPU by default; auto-detect CUDA
        try:
            _whisper_model = WhisperModel(
                model_size,
                device="cuda",
                compute_type="float16",
            )
            logger.info("Whisper loaded on CUDA GPU")
        except Exception:
            _whisper_model = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8",
                cpu_threads=4,
            )
            logger.info("Whisper loaded on CPU (int8, 4 threads)")

    return _whisper_model


def transcribe_whisper(audio_path: Path) -> TranscriptResult:
    """
    Transcribe audio using Groq API (whisper-large-v3) or fallback to local Whisper.
    Returns timestamped segments.
    """
    if settings.groq_api_key:
        logger.info(f"Transcribing with Groq API (whisper-large-v3): {audio_path.name}")
        try:
            with open(audio_path, "rb") as f:
                files = {"file": (audio_path.name, f, "audio/wav")}
                data = {
                    "model": "whisper-large-v3",
                    "response_format": "verbose_json",
                }
                headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
                
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        files=files,
                        data=data,
                        headers=headers,
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    segments = []
                    for seg in result.get("segments", []):
                        clean_text = clean_transcript_text(seg.get("text", ""))
                        if clean_text:
                            segments.append(TranscriptSegment(
                                start=seg.get("start", 0.0),
                                end=seg.get("end", 0.0),
                                text=clean_text
                            ))
                    
                    full_text = result.get("text", "")
                    detected_lang = result.get("language", "en")
                    
                    logger.info(
                        f"Groq transcription complete: {len(segments)} segments, "
                        f"language={detected_lang}"
                    )
                    
                    return TranscriptResult(
                        segments=segments,
                        full_text=full_text,
                        language=detected_lang,
                        engine="groq_whisper",
                    )
                else:
                    logger.error(f"Groq API error: {response.text}")
                    logger.info("Falling back to local whisper...")
        except Exception as e:
            logger.error(f"Groq API connection error: {e}")
            logger.info("Falling back to local whisper...")

    logger.info(f"Transcribing with local Whisper: {audio_path.name}")

    model = _get_whisper_model()
    segments_gen, info = model.transcribe(
        str(audio_path),
        beam_size=1,    # Greedy decoding is significantly faster on CPU
        language=None,  # Auto-detect
        vad_filter=True,  # Filter out silence
        vad_parameters=dict(
            min_silence_duration_ms=500,
        ),
    )

    segments = []
    texts = []
    for segment in segments_gen:
        clean_text = clean_transcript_text(segment.text)
        if clean_text:
            segments.append(TranscriptSegment(
                start=segment.start,
                end=segment.end,
                text=clean_text,
            ))
            texts.append(clean_text)

    full_text = " ".join(texts)
    detected_lang = info.language if info.language else "en"

    logger.info(
        f"Whisper transcription complete: {len(segments)} segments, "
        f"language={detected_lang}"
    )

    return TranscriptResult(
        segments=segments,
        full_text=full_text,
        language=detected_lang,
        engine="whisper",
    )


def transcribe(
    audio_path: Path,
    language: str = "auto",
) -> TranscriptResult:
    """
    Main transcription router.
    Routes to Whisper or Sarvam based on language setting.

    Args:
        audio_path: Path to the audio file (16kHz mono WAV)
        language: Language hint — "en", "hi", or "auto"

    Returns:
        TranscriptResult with segments and full text
    """
    return transcribe_whisper(audio_path)
