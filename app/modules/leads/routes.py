# app/modules/leads/routes.py

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.leads.services import LeadService
from app.shared.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/leads", tags=["Leads"])
service = LeadService()


@router.post("/")
def create_lead(data: dict, db: Session = Depends(get_db)):
    try:
        return service.create_lead(db, data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/")
def list_leads(
    status: Optional[str] = None,
    assigned_to: Optional[uuid.UUID] = None,
    created_by: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
):
    filters = {}
    if status:
        filters["status"] = status
    if assigned_to:
        filters["assigned_to"] = assigned_to
    if created_by:
        filters["created_by"] = created_by
    return service.list_leads(db, filters or None)


@router.get("/{lead_id}")
def get_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return service.get_lead(db, lead_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{lead_id}")
def update_lead(lead_id: uuid.UUID, data: dict, db: Session = Depends(get_db)):
    try:
        return service.update_lead(db, lead_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{lead_id}/assign")
def assign_lead(lead_id: uuid.UUID, data: dict, db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=422, detail="user_id is required")
    try:
        return service.assign_lead(db, lead_id, uuid.UUID(str(user_id)))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))