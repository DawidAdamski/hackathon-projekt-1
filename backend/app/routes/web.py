from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import JobCreate
from app.services.job_service import create_job, list_jobs
from app.tasks.fast_task import run_fast_task
from app.tasks.fail_task import run_fail_task
from app.tasks.slow_task import run_slow_task

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def web_index(request: Request, db: Session = Depends(get_db)):
    jobs = list_jobs(db, limit=100)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs,
        },
    )


@router.post("/jobs/create")
def web_create_job(
    request: Request,
    job_type: str = Form(...),
    db: Session = Depends(get_db),
):
    job_in = JobCreate(type=job_type, payload=None)
    job = create_job(db, job_in)

    if job.type == "fast":
        run_fast_task.delay(str(job.id))
    elif job.type == "fail":
        run_fail_task.delay(str(job.id))
    elif job.type == "slow":
        run_slow_task.delay(str(job.id))
    else:
        run_fast_task.delay(str(job.id))

    return RedirectResponse(url="/", status_code=303)
