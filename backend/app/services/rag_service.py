"""
VoxLens — RAG Service

Retrieval-Augmented Generation pipeline using LangChain LCEL.
Queries ChromaDB for relevant transcript chunks and generates grounded answers.
"""

import logging

from app.services.embedding_service import query_similar
from app.services.llm_service import generate_with_context

logger = logging.getLogger("voxlens.rag")


def query_meeting(meeting_id: str, question: str) -> dict:
    """
    RAG query over a meeting's transcript.

    1. Retrieve relevant chunks from ChromaDB
    2. Build context from retrieved chunks
    3. Generate a grounded answer using the LLM

    Args:
        meeting_id: The meeting to query
        question: User's question

    Returns:
        dict with keys: answer, sources
    """
    logger.info(f"RAG query for meeting {meeting_id}: {question[:100]}")

    # Step 1: Retrieve relevant chunks
    similar_chunks = query_similar(meeting_id, question, n_results=5)

    if not similar_chunks:
        return {
            "answer": (
                "I don't have enough context from the meeting transcript to answer "
                "this question. The meeting may not have been fully processed yet."
            ),
            "sources": [],
        }

    # Step 2: Build context from retrieved chunks
    context_parts = []
    sources = []
    for i, chunk in enumerate(similar_chunks):
        text = chunk["text"]
        metadata = chunk.get("metadata", {})
        distance = chunk.get("distance", 0)

        context_parts.append(f"[Segment {i + 1}]: {text}")
        sources.append({
            "chunk_index": metadata.get("chunk_index", i),
            "text": text[:200] + "..." if len(text) > 200 else text,
            "relevance": round(1 - distance, 3) if distance else 0,
        })

    context = "\n\n".join(context_parts)

    # Step 3: Generate grounded answer
    answer = generate_with_context(question, context)

    logger.info(f"RAG answer generated ({len(answer)} chars, {len(sources)} sources)")

    return {
        "answer": answer,
        "sources": sources,
    }
