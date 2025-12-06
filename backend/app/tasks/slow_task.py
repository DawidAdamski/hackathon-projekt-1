import time
from uuid import UUID

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.job_service import set_job_status


@celery_app.task(name="app.tasks.slow_task.run_slow_task")
def run_slow_task(job_id: str) -> None:
    db = SessionLocal()
    try:
        set_job_status(db, UUID(job_id), status="RUNNING")
        time.sleep(10)
        set_job_status(
            db,
            UUID(job_id),
            status="SUCCESS",
            result={"message": "Slow task finished after 10 seconds"},
        )
    finally:
        db.close()
