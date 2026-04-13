# app/modules/quotations/routes.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.quotations.services import QuotationService
from app.shared.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.post("/")
def create_quotation(data: dict, db: Session = Depends(get_db)):
    lead_id_raw = data.get("lead_id")
    try:
        lead_id = UUID(str(lead_id_raw))
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid lead_id")
    try:
        return QuotationService().create_quotation(db, lead_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{quotation_id}")
def get_quotation(quotation_id: UUID, db: Session = Depends(get_db)):
    try:
        return QuotationService().get_quotation(db, quotation_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{quotation_id}/versions")
def add_version(quotation_id: UUID, data: dict, db: Session = Depends(get_db)):
    try:
        return QuotationService().add_version(db, quotation_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{quotation_id}/versions")
def list_versions(quotation_id: UUID, db: Session = Depends(get_db)):
    try:
        return QuotationService().list_versions(db, quotation_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/versions/{version_id}/line-items")
def add_line_items(version_id: UUID, data: dict, db: Session = Depends(get_db)):
    items = data.get("items")
    if not isinstance(items, list):
        raise HTTPException(status_code=422, detail="items must be list")
    try:
        return QuotationService().add_line_items(db, version_id, items)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/versions/{version_id}/final")
def mark_final(version_id: UUID, db: Session = Depends(get_db)):
    try:
        return QuotationService().mark_final(db, version_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{quotation_id}/accept")
def accept_quotation(quotation_id: UUID, db: Session = Depends(get_db)):
    try:
        return QuotationService().accept_quotation(db, quotation_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))