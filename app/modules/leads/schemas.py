from __future__ import annotations
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class LeadCreate(BaseModel):
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class LeadTransition(BaseModel):
    status: str
    notes: Optional[str] = None


class LeadAssign(BaseModel):
    user_id: UUID


class LeadResponse(BaseModel):
    id: UUID
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True
