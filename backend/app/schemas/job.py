from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class JobBase(BaseModel):
    type: str = Field(..., description="Type of job, e.g. fast, fail, slow")
    payload: Optional[dict[str, Any]] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None


class JobOut(JobBase):
    id: UUID
    status: str
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
