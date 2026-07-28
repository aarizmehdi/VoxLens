"""
VoxLens — Report Endpoint

Retrieve the generated meeting intelligence report.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting, SummaryReport
from app.schemas import SummaryReportResponse

router = APIRouter()


@router.get(
    "/report/{meeting_id}",
    response_model=SummaryReportResponse,
    tags=["Reports"],
)
async def get_report(meeting_id: str, db: Session = Depends(get_db)):
    """Get the summary report for a meeting."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    report = (
        db.query(SummaryReport)
        .filter(SummaryReport.meeting_id == meeting_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not yet available. The meeting may still be processing.",
        )

    return report
