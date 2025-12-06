from uuid import UUID

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.job_service import set_job_status


@celery_app.task(name="app.tasks.fail_task.run_fail_task")
def run_fail_task(job_id: str) -> None:
    db = SessionLocal()
    try:
        set_job_status(
            db,
            UUID(job_id),
            status="FAILED",
            error_message="Intentional failure for testing",
        )
        raise RuntimeError("Intentional failure in Celery task")
    finally:
        db.close()
