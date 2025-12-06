from uuid import UUID

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.job_service import set_job_status


@celery_app.task(name="app.tasks.fast_task.run_fast_task")
def run_fast_task(job_id: str) -> None:
    db = SessionLocal()
    try:
        set_job_status(
            db,
            UUID(job_id),
            status="SUCCESS",
            result={"message": "Fast task completed instantly"},
        )
    finally:
        db.close()
