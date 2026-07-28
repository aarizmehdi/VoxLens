"""
VoxLens — LLM Service

Wrapper around the DeepSeek API using the OpenAI-compatible SDK.
Provides both regular and streaming completions.
"""

import json
import logging

from openai import OpenAI

from app.config import settings

logger = logging.getLogger("voxlens.llm")

# Lazy-initialized client
_client = None


def _get_client() -> OpenAI:
    """Get or create the OpenAI client configured for DeepSeek."""
    global _client
    if _client is None:
        if not settings.deepseek_api_key:
            raise RuntimeError(
                "DeepSeek API key not configured. "
                "Set DEEPSEEK_API_KEY in your .env file."
            )
        _client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        logger.info(f"DeepSeek client initialized (model: {settings.deepseek_model})")
    return _client


def generate(
    prompt: str,
    system_prompt: str = "You are a helpful meeting analysis assistant.",
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    """
    Generate a completion from the DeepSeek LLM.

    Args:
        prompt: The user prompt
        system_prompt: System instruction
        temperature: Sampling temperature (lower = more deterministic)
        max_tokens: Maximum response tokens

    Returns:
        The generated text response
    """
    client = _get_client()

    logger.debug(f"LLM request: {prompt[:100]}...")

    response = client.chat.completions.create(
        model=settings.deepseek_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )

    result = response.choices[0].message.content
    logger.debug(f"LLM response: {result[:100]}...")
    return result


def generate_json(
    prompt: str,
    system_prompt: str = "You are a helpful meeting analysis assistant. Always respond with valid JSON.",
    temperature: float = 0.2,
    max_tokens: int = 4096,
) -> dict:
    """
    Generate a JSON response from the LLM.
    Parses the response and handles markdown code fences.

    Args:
        prompt: The user prompt (should request JSON output)
        system_prompt: System instruction

    Returns:
        Parsed JSON as a dictionary
    """
    raw = generate(prompt, system_prompt, temperature, max_tokens)

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        logger.error(f"Raw response: {raw}")
        # Attempt to find JSON in the response
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"LLM did not return valid JSON: {e}")


def generate_with_context(
    question: str,
    context: str,
    system_prompt: str | None = None,
    temperature: float = 0.3,
) -> str:
    """
    Generate an answer grounded in provided context (for RAG).

    Args:
        question: User's question
        context: Retrieved transcript context
        system_prompt: Optional custom system prompt

    Returns:
        Grounded answer text
    """
    if system_prompt is None:
        system_prompt = (
            "You are VoxLens, an AI meeting assistant. Answer questions based ONLY "
            "on the provided meeting transcript context. If the answer cannot be found "
            "in the context, say so honestly. Be concise, accurate, and helpful. "
            "When referencing specific parts of the meeting, mention the relevant details."
        )

    prompt = f"""Based on the following meeting transcript context, answer the user's question.

CONTEXT:
{context}

QUESTION:
{question}

Provide a clear, concise answer grounded in the meeting content above."""

    return generate(prompt, system_prompt, temperature)
