"""
Celery configuration for background tasks.
"""
from celery import Celery
from .config import settings

# Create Celery app
celery_app = Celery(
    "akta",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.process_pdf": {"queue": "pdf_processing"},
    "app.tasks.generate_embeddings": {"queue": "ai_processing"},
}

if __name__ == "__main__":
    celery_app.start()