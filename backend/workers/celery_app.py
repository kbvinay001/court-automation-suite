"""
Celery Application - Async task queue configuration for background processing.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Redis broker/backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "court_automation",
    broker=REDIS_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["workers.tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="Asia/Kolkata",
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # Soft limit at 4 minutes
    task_acks_late=True,  # Acknowledge after task completes
    worker_prefetch_multiplier=1,  # One task at a time per worker

    # Retry settings
    task_default_retry_delay=60,  # Retry after 1 minute
    task_max_retries=3,

    # Result expiry
    result_expires=3600,  # Results expire after 1 hour

    # Periodic tasks (beat schedule)
    beat_schedule={
        # Scrape cause lists every morning at 6:30 AM IST
        "scrape-daily-causelists": {
            "task": "workers.tasks.scrape_daily_causelists",
            "schedule": crontab(hour=6, minute=30),
            "args": (),
        },
        # Check tracked cases for updates every 2 hours
        "check-tracked-cases": {
            "task": "workers.tasks.check_tracked_case_updates",
            "schedule": crontab(minute=0, hour="*/2"),
            "args": (),
        },
        # Send hearing reminders at 8 AM
        "send-hearing-reminders": {
            "task": "workers.tasks.send_hearing_reminders",
            "schedule": crontab(hour=8, minute=0),
            "args": (),
        },
        # Send daily digest at 7 PM
        "send-daily-digest": {
            "task": "workers.tasks.send_daily_digest",
            "schedule": crontab(hour=19, minute=0),
            "args": (),
        },
        # Clean up old cache entries weekly
        "cleanup-cache": {
            "task": "workers.tasks.cleanup_old_data",
            "schedule": crontab(hour=2, minute=0, day_of_week="sunday"),
            "args": (),
        },
    },
)

if __name__ == "__main__":
    celery_app.start()
