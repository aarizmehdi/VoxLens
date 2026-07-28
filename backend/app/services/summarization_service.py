"""
VoxLens — Summarization Service

Generates structured meeting intelligence from transcripts:
- Meeting title
- Concise summary
- Key bullet points & takeaways
- Action items (owner, deadline, task)
- Key decisions
- Open questions / follow-ups
"""

import logging
from dataclasses import dataclass

from app.services.llm_service import generate, generate_json

logger = logging.getLogger("voxlens.summarization")


@dataclass
class MeetingReport:
    """Complete meeting intelligence report."""
    title: str
    summary: str
    bullet_points: list[str]
    key_takeaways: list[str]
    action_items: list[dict]  # [{task, owner, deadline}]
    decisions: list[str]
    open_questions: list[str]


def generate_meeting_title(transcript: str) -> str:
    """Generate a concise, descriptive title for the meeting."""
    # Truncate transcript to save tokens
    excerpt = transcript[:3000]

    prompt = f"""Based on this meeting transcript excerpt, generate a short, descriptive title 
(5-10 words max) that captures the main topic or purpose of the meeting.

TRANSCRIPT:
{excerpt}

Respond with ONLY the title text, nothing else."""

    title = generate(prompt, temperature=0.3, max_tokens=50)
    return title.strip().strip('"').strip("'")


def generate_summary(transcript: str) -> dict:
    """
    Generate a comprehensive summary with bullet points and takeaways.

    Returns:
        dict with keys: summary, bullet_points, key_takeaways
    """
    prompt = f"""Analyze this meeting transcript and generate a structured summary.

TRANSCRIPT:
{transcript}

Respond with a JSON object containing:
{{
    "summary": "A concise 2-4 sentence overview of the meeting's purpose and main outcomes",
    "bullet_points": ["Key point 1", "Key point 2", ...],
    "key_takeaways": ["Most important takeaway 1", "Most important takeaway 2", ...]
}}

Rules:
- The summary should be informative, not generic
- Include 4-8 bullet points covering the main discussion topics
- Include 2-4 key takeaways that highlight the most important outcomes
- Be specific — reference actual topics, names, and decisions mentioned
- Do NOT make up information not present in the transcript"""

    return generate_json(prompt)


def extract_action_items(transcript: str) -> list[dict]:
    """
    Extract action items with owners and deadlines.

    Returns:
        list of dicts with keys: task, owner, deadline
    """
    prompt = f"""Extract all action items, tasks, and commitments from this meeting transcript.

TRANSCRIPT:
{transcript}

Respond with a JSON object:
{{
    "action_items": [
        {{
            "task": "Description of what needs to be done",
            "owner": "Person responsible (use 'Unknown' if not mentioned)",
            "deadline": "Due date or timeframe (use 'Not specified' if not mentioned)"
        }}
    ]
}}

Rules:
- Include ALL tasks, to-dos, and commitments mentioned
- If someone says "I'll do X" or "Let's do Y", that's an action item
- Be specific about the task description
- Use "Unknown" for owner if not clear who is responsible
- Use "Not specified" for deadline if no timeframe mentioned
- If no action items exist, return an empty list
- Do NOT invent action items not discussed in the meeting"""

    result = generate_json(prompt)
    return result.get("action_items", [])


def extract_decisions(transcript: str) -> list[str]:
    """Extract key decisions made during the meeting."""
    prompt = f"""Extract all key decisions made during this meeting.

TRANSCRIPT:
{transcript}

Respond with a JSON object:
{{
    "decisions": ["Decision 1", "Decision 2", ...]
}}

Rules:
- Include decisions that were agreed upon or finalized
- Be specific about what was decided
- If no clear decisions were made, return an empty list
- Do NOT include tentative ideas or proposals unless they were confirmed"""

    result = generate_json(prompt)
    return result.get("decisions", [])


def extract_open_questions(transcript: str) -> list[str]:
    """Extract unresolved questions and follow-ups."""
    prompt = f"""Extract all unresolved questions, open issues, and items needing follow-up from this meeting.

TRANSCRIPT:
{transcript}

Respond with a JSON object:
{{
    "open_questions": ["Question or issue 1", "Question or issue 2", ...]
}}

Rules:
- Include questions that were raised but not fully answered
- Include topics that need further investigation or discussion
- Include items explicitly marked for follow-up
- If no open questions exist, return an empty list"""

    result = generate_json(prompt)
    return result.get("open_questions", [])


def generate_full_report(transcript: str) -> MeetingReport:
    """
    Generate a complete meeting intelligence report.
    Orchestrates all extraction steps.

    Args:
        transcript: Full meeting transcript text

    Returns:
        MeetingReport with all extracted intelligence
    """
    logger.info("Generating full meeting report...")

    # Truncate very long transcripts to stay within token limits
    max_chars = 30000
    if len(transcript) > max_chars:
        logger.warning(
            f"Transcript is {len(transcript)} chars, truncating to {max_chars}"
        )
        transcript = transcript[:max_chars] + "\n\n[Transcript truncated for analysis]"

    # Generate each component
    title = generate_meeting_title(transcript)
    logger.info(f"Title: {title}")

    summary_data = generate_summary(transcript)
    logger.info("Summary generated")

    action_items = extract_action_items(transcript)
    logger.info(f"Action items: {len(action_items)}")

    decisions = extract_decisions(transcript)
    logger.info(f"Decisions: {len(decisions)}")

    open_questions = extract_open_questions(transcript)
    logger.info(f"Open questions: {len(open_questions)}")

    report = MeetingReport(
        title=title,
        summary=summary_data.get("summary", ""),
        bullet_points=summary_data.get("bullet_points", []),
        key_takeaways=summary_data.get("key_takeaways", []),
        action_items=action_items,
        decisions=decisions,
        open_questions=open_questions,
    )

    logger.info("Full meeting report generated successfully")
    return report
