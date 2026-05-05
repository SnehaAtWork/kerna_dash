# app/modules/projects/schemas.py

from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: UUID
    client_id: UUID
    status: str
    health_score_internal: int
    health_status_client: str
    internal_deadline: Optional[datetime] = None
    client_deadline: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
