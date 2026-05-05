from __future__ import annotations
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class QuotationCreate(BaseModel):
    lead_id: UUID
    title: Optional[str] = None
    status: Optional[str] = "DRAFT"


class QuotationResponse(BaseModel):
    id: UUID
    lead_id: UUID
    status: str
    title: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class VersionCreate(BaseModel):
    total: Optional[float] = 0.0
    notes: Optional[str] = None


class VersionResponse(BaseModel):
    id: UUID
    quotation_id: UUID
    version_number: int
    is_final: bool
    subtotal: float
    discount: float
    total: float
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class LineItemCreate(BaseModel):
    items: list[dict]


class QuotationFeedback(BaseModel):
    feedback: Optional[str] = None


class QuotationReject(BaseModel):
    reason: str


class QuotationRevision(BaseModel):
    feedback: Optional[str] = None
