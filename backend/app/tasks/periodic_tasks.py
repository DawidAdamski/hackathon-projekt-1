from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.schemas.job import JobCreate
from app.services.job_service import create_job


@celery_app.task(name="app.tasks.periodic.schedule_slow_job")
def schedule_slow_job():
    from app.tasks.slow_task import run_slow_task

    """
    Task odpalany przez Celery Beat – tworzy job i uruchamia prawdziwy task.
    Chodzi o to ze on tworzy job id w bazie z ID i potem przekazuje go do taska
    """
    db = SessionLocal()
    try:
        job_in = JobCreate(type="slow", payload={"source": "beat"})
        job = create_job(db, job_in)
        run_slow_task.delay(str(job.id))
    finally:
        db.close()


@celery_app.task(name="app.tasks.periodic.schedule_fast_job")
def schedule_fast_job():
    # NOTE: UWAGA NA CYRKOWE IMPORTY
    from app.tasks.fast_task import run_fast_task

    """
    Task odpalany przez Celery Beat – tworzy job i uruchamia prawdziwy task.
    Chodzi o to ze on tworzy job id w bazie z ID i potem przekazuje go do taska
    """
    db = SessionLocal()
    try:
        job_in = JobCreate(type="fast", payload={"source": "beat"})
        job = create_job(db, job_in)
        run_fast_task.delay(str(job.id))
    finally:
        db.close()
