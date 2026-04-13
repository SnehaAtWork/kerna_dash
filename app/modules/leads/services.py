import uuid

from sqlalchemy.orm import Session

from app.modules.leads.models import Lead
from app.modules.leads.repositories import LeadRepository
from app.shared.exceptions import NotFoundError, ValidationError


class LeadService:

    def __init__(self):
        self.repository = LeadRepository()

    def create_lead(self, db: Session, data: dict) -> Lead:
        if not data.get("company_name"):
            raise ValidationError("company_name is required")
        return self.repository.create(db, data)

    def get_lead(self, db: Session, lead_id: uuid.UUID) -> Lead:
        lead = self.repository.get_by_id(db, lead_id)
        if not lead:
            raise NotFoundError("Lead", lead_id)
        return lead

    def update_lead(self, db: Session, lead_id: uuid.UUID, data: dict) -> Lead:
        lead = self.get_lead(db, lead_id)
        return self.repository.update(db, lead, data)

    def assign_lead(self, db: Session, lead_id: uuid.UUID, user_id: uuid.UUID) -> Lead:
        if not user_id:
            raise ValidationError("user_id is required for assignment")
        lead = self.get_lead(db, lead_id)
        return self.repository.assign(db, lead, user_id)

    def list_leads(self, db: Session, filters: dict | None = None) -> list[Lead]:
        return self.repository.list(db, filters)