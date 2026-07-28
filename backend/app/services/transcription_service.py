"""
VoxLens — Transcription Service

Routes transcription to the appropriate engine:
- faster-whisper for English (local, free)
- Sarvam AI for Hindi/Hinglish (API, better quality for Indian languages)

Falls back to Whisper if Sarvam is unavailable.
"""

import logging
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
    Transcribe audio using local faster-whisper.
    Returns timestamped segments.
    """
    logger.info(f"Transcribing with Whisper: {audio_path.name}")

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


def transcribe_sarvam(audio_path: Path) -> TranscriptResult:
    """
    Transcribe audio using Sarvam AI API.
    Best for Hindi/Hinglish content.
    """
    if not settings.sarvam_api_key:
        raise RuntimeError("Sarvam API key not configured")

    logger.info(f"Transcribing with Sarvam AI: {audio_path.name}")

    from sarvamai import SarvamAI

    client = SarvamAI(api_subscription_key=settings.sarvam_api_key)

    with open(audio_path, "rb") as audio_file:
        response = client.speech_to_text(
            file=audio_file,
            model=settings.sarvam_model,
            mode="codemix",  # Best for Hinglish
        )

    # Parse Sarvam response into segments
    segments = []
    if hasattr(response, "segments") and response.segments:
        for seg in response.segments:
            segments.append(TranscriptSegment(
                start=getattr(seg, "start", 0.0),
                end=getattr(seg, "end", 0.0),
                text=clean_transcript_text(getattr(seg, "text", "")),
            ))
    elif hasattr(response, "text") and response.text:
        # Fallback: single segment
        segments.append(TranscriptSegment(
            start=0.0,
            end=0.0,
            text=clean_transcript_text(response.text),
        ))

    full_text = " ".join(s.text for s in segments)

    logger.info(f"Sarvam transcription complete: {len(segments)} segments")

    return TranscriptResult(
        segments=segments,
        full_text=full_text,
        language="hi",
        engine="sarvam",
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
    # If Hindi explicitly requested and Sarvam is available, use it
    if language == "hi" and settings.sarvam_api_key:
        try:
            return transcribe_sarvam(audio_path)
        except Exception as e:
            logger.warning(f"Sarvam transcription failed, falling back to Whisper: {e}")

    # Default: use Whisper
    result = transcribe_whisper(audio_path)

    # If auto-detect and the result looks Hindi, try Sarvam for better quality
    if language == "auto" and settings.sarvam_api_key:
        detected = estimate_language(result.full_text)
        if detected == "hi":
            logger.info("Hindi detected — retrying with Sarvam AI for better quality")
            try:
                return transcribe_sarvam(audio_path)
            except Exception as e:
                logger.warning(f"Sarvam retry failed: {e}")

    return result
