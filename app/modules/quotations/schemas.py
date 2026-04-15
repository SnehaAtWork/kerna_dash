from __future__ import annotations
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class QuotationCreate(BaseModel):
    lead_id: UUID
    data: Optional[dict] = None


class QuotationResponse(BaseModel):
    id: UUID
    lead_id: UUID
    status: str

    class Config:
        from_attributes = True


class VersionCreate(BaseModel):
    data: Optional[dict] = None


class VersionResponse(BaseModel):
    id: UUID
    quotation_id: UUID
    version_number: int
    is_final: bool
    status: str

    class Config:
        from_attributes = True


class LineItemCreate(BaseModel):
    items: list[dict]