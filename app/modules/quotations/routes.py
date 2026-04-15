# app/modules/quotations/routes.py

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.quotations.services import QuotationService
from app.modules.quotations.schemas import QuotationCreate, VersionCreate, LineItemCreate

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.post("/")
def create_quotation(data: QuotationCreate, db: Session = Depends(get_db)):
    return QuotationService().create_quotation(db, data.lead_id, data.dict(exclude={"lead_id"}))


@router.get("/{quotation_id}")
def get_quotation(quotation_id: UUID, db: Session = Depends(get_db)):
    return QuotationService().get_quotation(db, quotation_id)


@router.post("/{quotation_id}/versions")
def add_version(quotation_id: UUID, data: VersionCreate, db: Session = Depends(get_db)):
    return QuotationService().add_version(db, quotation_id, data.dict())


@router.get("/{quotation_id}/versions")
def list_versions(quotation_id: UUID, db: Session = Depends(get_db)):
    return QuotationService().list_versions(db, quotation_id)


@router.post("/versions/{version_id}/line-items")
def add_line_items(version_id: UUID, data: LineItemCreate, db: Session = Depends(get_db)):
    return QuotationService().add_line_items(db, version_id, data.items)


@router.post("/versions/{version_id}/final")
def mark_final(version_id: UUID, db: Session = Depends(get_db)):
    return QuotationService().mark_final(db, version_id)


@router.post("/{quotation_id}/accept")
def accept_quotation(quotation_id: UUID, db: Session = Depends(get_db)):
    return QuotationService().accept_quotation(db, quotation_id)