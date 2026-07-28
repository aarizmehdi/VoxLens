"""
VoxLens — API Router

Central router that aggregates all API endpoint modules.
"""

from fastapi import APIRouter

from app.api import health, process, jobs, meetings, transcripts, reports, chat, export

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(process.router)
api_router.include_router(jobs.router)
api_router.include_router(meetings.router)
api_router.include_router(transcripts.router)
api_router.include_router(reports.router)
api_router.include_router(chat.router)
api_router.include_router(export.router)
