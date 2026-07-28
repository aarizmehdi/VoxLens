"""
VoxLens — Celery Application

Configures Celery with Redis as the broker and result backend.
"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "voxlens",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # One task at a time for heavy processing
    task_soft_time_limit=1800,  # 30 minutes
    task_time_limit=3600,  # 1 hour hard limit
)
