# app/modules/quotations/routes.py

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.modules.quotations.services import QuotationService
from app.modules.quotations.schemas import (
    QuotationCreate,
    VersionCreate,
    LineItemCreate,
    QuotationFeedback,
    QuotationReject,
    QuotationRevision,
)

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.get("/")
def list_quotations(
    lead_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return QuotationService().list_quotations(db, lead_id)


@router.post("/")
def create_quotation(data: QuotationCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().create_quotation(db, data.lead_id, data.dict(exclude={"lead_id"}))


@router.get("/{quotation_id}")
def get_quotation(quotation_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().get_quotation(db, quotation_id)


@router.post("/{quotation_id}/versions")
def add_version(quotation_id: UUID, data: VersionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().add_version(db, quotation_id, data.dict())


@router.get("/{quotation_id}/versions")
def list_versions(quotation_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().list_versions(db, quotation_id)


@router.post("/versions/{version_id}/line-items")
def add_line_items(version_id: UUID, data: LineItemCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().add_line_items(db, version_id, data.items)


@router.post("/versions/{version_id}/final")
def mark_final(version_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().mark_final(db, version_id)


@router.post("/{quotation_id}/submit")
def submit_quotation(quotation_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().submit_quotation(db, quotation_id)


@router.post("/{quotation_id}/viewed")
def mark_viewed(quotation_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().mark_viewed(db, quotation_id)


@router.post("/{quotation_id}/awaiting-response")
def mark_awaiting_response(quotation_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().mark_awaiting_response(db, quotation_id)


@router.post("/{quotation_id}/negotiation")
def mark_negotiation(quotation_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().mark_negotiation(db, quotation_id)


@router.post("/{quotation_id}/approve")
def approve_quotation(quotation_id: UUID, data: QuotationFeedback, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().approve_quotation(db, quotation_id, data.feedback)


@router.post("/{quotation_id}/reject")
def reject_quotation(quotation_id: UUID, data: QuotationReject, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().reject_quotation(db, quotation_id, data.reason)


@router.post("/{quotation_id}/convert")
def convert_quotation(quotation_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().convert_quotation(db, quotation_id)


@router.post("/{quotation_id}/revision")
def create_revision(quotation_id: UUID, data: QuotationRevision, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().create_revision(db, quotation_id, data.feedback)


@router.post("/{quotation_id}/accept")
def accept_quotation(quotation_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return QuotationService().accept_quotation(db, quotation_id, current_user)
