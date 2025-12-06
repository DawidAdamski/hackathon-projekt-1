from app.core.config import get_settings
from celery import Celery

settings = get_settings()

celery_app = Celery(
    "hacknation_jobs",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.task_routes = {
    "app.tasks.fast_task.run_fast_task": {"queue": "fast"},
    "app.tasks.fail_task.run_fail_task": {"queue": "fail"},
    "app.tasks.slow_task.run_slow_task": {"queue": "slow"},
}

import app.tasks.fail_task  # noqa
import app.tasks.fast_task  # noqa
import app.tasks.periodic_tasks  # noqa ważne – żeby Celery go załadował
import app.tasks.slow_task  # noqa
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "run-periodic-slow-job": {
        "task": "app.tasks.periodic.schedule_fast_job",
        "schedule": 10.0,  # co 30 sekund
    }
}
