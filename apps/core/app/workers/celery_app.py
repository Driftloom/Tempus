"""Celery application configuration."""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "tempus",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.tasks.email_tasks",
        "app.workers.tasks.notification_tasks",
        "app.workers.tasks.memory_tasks",
        "app.workers.tasks.agent_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
    task_retry_backoff=True,
    task_retry_backoff_max=600,
    task_retry_jitter=True,
)
