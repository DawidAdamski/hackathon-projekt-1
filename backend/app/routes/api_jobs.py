from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import JobCreate, JobOut
from app.services.job_service import create_job, get_job, list_jobs
from app.tasks.fast_task import run_fast_task
from app.tasks.fail_task import run_fail_task
from app.tasks.slow_task import run_slow_task

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobOut])
def api_list_jobs(db: Session = Depends(get_db)):
    return list_jobs(db)


@router.get("/{job_id}", response_model=JobOut)
def api_get_job(job_id: UUID, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=JobOut)
def api_create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    job = create_job(db, job_in)

    if job.type == "fast":
        run_fast_task.delay(str(job.id))
    elif job.type == "fail":
        run_fail_task.delay(str(job.id))
    elif job.type == "slow":
        run_slow_task.delay(str(job.id))
    else:
        run_fast_task.delay(str(job.id))

    return job
