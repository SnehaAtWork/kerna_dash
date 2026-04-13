import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.leads.models import Lead


class LeadRepository:

    def create(self, db: Session, data: dict) -> Lead:
        lead = Lead(**data)
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    def get_by_id(self, db: Session, lead_id: uuid.UUID) -> Lead | None:
        return db.get(Lead, lead_id)

    def list(self, db: Session, filters: dict | None = None) -> list[Lead]:
        stmt = select(Lead)
        if filters:
            if status := filters.get("status"):
                stmt = stmt.where(Lead.status == status)
            if assigned_to := filters.get("assigned_to"):
                stmt = stmt.where(Lead.assigned_to == assigned_to)
            if created_by := filters.get("created_by"):
                stmt = stmt.where(Lead.created_by == created_by)
        return db.execute(stmt).scalars().all()

    def update(self, db: Session, lead: Lead, data: dict) -> Lead:
        for key, value in data.items():
            setattr(lead, key, value)
        db.commit()
        db.refresh(lead)
        return lead

    def assign(self, db: Session, lead: Lead, user_id: uuid.UUID) -> Lead:
        lead.assigned_to = user_id
        db.commit()
        db.refresh(lead)
        return lead