from fastapi import APIRouter

from app.routes import api_jobs, web

api_router = APIRouter()
api_router.include_router(api_jobs.router, prefix="/jobs")

web_router = APIRouter()
web_router.include_router(web.router)
