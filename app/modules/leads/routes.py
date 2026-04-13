# app/modules/leads/routes.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.leads.services import LeadService
from app.shared.exceptions import NotFoundError, ValidationError

from typing import Optional

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("/")
def create_lead(data: dict, db: Session = Depends(get_db)):
    try:
        return LeadService().create_lead(db, data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{lead_id}")
def get_lead(lead_id: UUID, db: Session = Depends(get_db)):
    try:
        return LeadService().get_lead(db, lead_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
def list_leads(
    status: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    created_by: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    filters = {}
    if status is not None:
        filters["status"] = status
    if assigned_to is not None:
        filters["assigned_to"] = assigned_to
    if created_by is not None:
        filters["created_by"] = created_by
    return LeadService().list_leads(db, filters or None)


@router.patch("/{lead_id}")
def update_lead(lead_id: UUID, data: dict, db: Session = Depends(get_db)):
    try:
        return LeadService().update_lead(db, lead_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{lead_id}/assign")
def assign_lead(lead_id: UUID, data: dict, db: Session = Depends(get_db)):
    try:
        raw = data.get("user_id")
        user_id = UUID(str(raw))
    except (ValueError, AttributeError):
        raise HTTPException(status_code=422, detail="Invalid user_id")
    try:
        return LeadService().assign_lead(db, lead_id, user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))