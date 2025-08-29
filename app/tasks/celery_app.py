from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "parenting_automation",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.daily_content",
        "app.tasks.engagement_monitor",
        "app.tasks.user_interaction"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    result_expires=3600,  # 1 hour
    beat_schedule={
        "daily-content-generation": {
            "task": "app.tasks.daily_content.generate_daily_content",
            "schedule": 3600.0,  # Every hour
        },
        "engagement-monitoring": {
            "task": "app.tasks.engagement_monitor.monitor_engagement",
            "schedule": 1800.0,  # Every 30 minutes
        },
        "weekly-content-batch": {
            "task": "app.tasks.daily_content.generate_weekly_content",
            "schedule": 604800.0,  # Every week
        },
    }
)
