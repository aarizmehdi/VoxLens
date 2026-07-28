"""
VoxLens — Chat Endpoint

RAG-based chat over meeting content.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting, ChatMessage
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Ask a question about a meeting.
    Uses RAG to find relevant transcript chunks and generate a grounded answer.
    """
    meeting = db.query(Meeting).filter(Meeting.id == request.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Meeting is not ready for chat. Current status: {meeting.status}",
        )

    # Save user message
    user_msg = ChatMessage(
        meeting_id=request.meeting_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.commit()

    # Query RAG pipeline
    try:
        from app.services.rag_service import query_meeting

        result = query_meeting(request.meeting_id, request.message)
        answer = result["answer"]
        sources = result.get("sources", [])
    except Exception as e:
        answer = f"I encountered an error while searching the meeting content: {str(e)}"
        sources = []

    # Save assistant message
    assistant_msg = ChatMessage(
        meeting_id=request.meeting_id,
        role="assistant",
        content=answer,
        sources=sources,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(
        message=ChatMessageResponse.model_validate(assistant_msg),
        sources=sources,
    )


@router.get(
    "/chat/{meeting_id}/history",
    response_model=list[ChatMessageResponse],
    tags=["Chat"],
)
async def get_chat_history(meeting_id: str, db: Session = Depends(get_db)):
    """Get the chat history for a meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.meeting_id == meeting_id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    return [ChatMessageResponse.model_validate(m) for m in messages]
