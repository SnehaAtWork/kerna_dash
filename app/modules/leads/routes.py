# app/modules/leads/routes.py

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.leads.services import LeadService
from app.modules.leads.schemas import LeadCreate, LeadUpdate, LeadAssign

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("/")
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    return LeadService().create_lead(db, data.dict())


@router.get("/{lead_id}")
def get_lead(lead_id: UUID, db: Session = Depends(get_db)):
    return LeadService().get_lead(db, lead_id)


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
def update_lead(lead_id: UUID, data: LeadUpdate, db: Session = Depends(get_db)):
    return LeadService().update_lead(db, lead_id, data.dict(exclude_unset=True))


@router.post("/{lead_id}/assign")
def assign_lead(lead_id: UUID, data: LeadAssign, db: Session = Depends(get_db)):
    return LeadService().assign_lead(db, lead_id, data.user_id)