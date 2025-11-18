from celery import Celery
from celery.schedules import crontab
from app.config import settings


celery_app = Celery(
    "vsl_pipeline",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


celery_app.conf.update(
    task_default_queue="default",
    include=[
        "app.workers.tasks_test",
        "app.workers.tasks_download",
        "app.workers.tasks_transcription",
        # "app.workers.tasks_categorization",
        "app.workers.pipeline_orchestrator",
        "app.workers.tasks_ingest",  
    ],
)

if settings.enable_ingest_scheduler:
    # 03:00 da manhã (horário do servidor)
        celery_app.conf.beat_schedule = {
        "process-pending-urls-daily": {
            "task": "app.workers.tasks_ingest.process_pending_urls",
            "schedule": crontab(hour=3, minute=0),
            "args": (200,),  # batch_size = 200
        },
    }
else:
    celery_app.conf.beat_schedule = {}