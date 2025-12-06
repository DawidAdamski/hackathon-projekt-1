from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


def create_job(db: Session, job_in: JobCreate) -> Job:
    job = Job(type=job_in.type, payload=job_in.payload, status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: UUID) -> Optional[Job]:
    stmt = select(Job).where(Job.id == job_id)
    return db.scalar(stmt)


def list_jobs(db: Session, limit: int = 50) -> Iterable[Job]:
    stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
    return db.scalars(stmt).all()


def update_job(db: Session, job: Job, job_in: JobUpdate) -> Job:
    data = job_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


def set_job_status(
    db: Session,
    job_id: UUID,
    status: str,
    result: Optional[dict] = None,
    error_message: Optional[str] = None,
) -> Optional[Job]:
    job = get_job(db, job_id)
    if not job:
        return None
    job.status = status
    if result is not None:
        job.result = result
    if error_message is not None:
        job.error_message = error_message
    db.commit()
    db.refresh(job)
    return job
