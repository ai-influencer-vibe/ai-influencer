"""Celery application bootstrap used by workers and periodic jobs."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_influencer_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="app.workers.ping")
def ping() -> str:
    """Return a small response used to validate the worker wiring."""

    return "pong"
