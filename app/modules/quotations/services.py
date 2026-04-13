import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.clients.models import Client, Project
from app.modules.clients.repositories import ClientRepository, ProjectRepository
from app.modules.leads.models import Lead
from app.modules.quotations.models import Quotation, QuotationLineItem, QuotationVersion
from app.modules.quotations.repositories import QuotationRepository
from app.shared.exceptions import NotFoundError, ValidationError


class QuotationService:

    def __init__(self):
        self.repository = QuotationRepository()
        self.client_repository = ClientRepository()
        self.project_repository = ProjectRepository()

    def create_quotation(self, db: Session, lead_id: uuid.UUID, data: dict) -> Quotation:
        if not lead_id:
            raise ValidationError("lead_id is required")
        payload = {**data, "lead_id": lead_id, "status": "DRAFT"}
        return self.repository.create_quotation(db, payload)

    def get_quotation(self, db: Session, quotation_id: uuid.UUID) -> Quotation:
        quotation = self.repository.get_quotation(db, quotation_id)
        if not quotation:
            raise NotFoundError("Quotation", quotation_id)
        return quotation

    def add_version(self, db: Session, quotation_id: uuid.UUID, data: dict) -> QuotationVersion:
        self.get_quotation(db, quotation_id)
        latest = self.repository.get_latest_version(db, quotation_id)
        next_number = (latest.version_number + 1) if latest else 1
        payload = {**data, "quotation_id": quotation_id, "version_number": next_number, "is_final": False}
        return self.repository.create_version(db, payload)

    def add_line_items(self, db: Session, version_id: uuid.UUID, items: list[dict]) -> list[QuotationLineItem]:
        if not items:
            raise ValidationError("At least one line item is required")
        version = self.repository.get_version(db, version_id)
        if not version:
            raise NotFoundError("QuotationVersion", version_id)
        clean_items = []
        for item in items:
            qty = item.get("quantity")
            price = item.get("unit_price")
            if not qty or qty <= 0:
                raise ValidationError("Each line item must have quantity > 0")
            if price is None:
                raise ValidationError("Each line item must have a unit_price")
            total = Decimal(str(price)) * qty
            clean_items.append({**item, "total": total})
        return self.repository.create_line_items(db, version_id, clean_items)

    def list_versions(self, db: Session, quotation_id: uuid.UUID) -> list[QuotationVersion]:
        self.get_quotation(db, quotation_id)
        return self.repository.get_versions(db, quotation_id)

    def mark_final(self, db: Session, version_id: uuid.UUID) -> QuotationVersion:
        version = self.repository.get_version(db, version_id)
        if not version:
            raise NotFoundError("QuotationVersion", version_id)
        self.repository.unset_final_versions(db, version.quotation_id)
        return self.repository.set_version_final(db, version)

    def accept_quotation(self, db: Session, quotation_id: uuid.UUID) -> dict:
        # TODO: wrap in single transaction (client + project + quotation update)
        quotation = self.get_quotation(db, quotation_id)

        # idempotency: already accepted
        if quotation.status == "ACCEPTED":
            lead: Lead = quotation.lead
            existing_client = self.client_repository.get_by_company_name(
                db, lead.company_name.strip().lower()
            ) if lead else None
            existing_project = (
                self.project_repository.get_latest_by_client_id(db, existing_client.id)
                if existing_client else None
            )
            return {"quotation": quotation, "project": existing_project}

        final = self.repository.get_final_version(db, quotation_id)
        if not final:
            raise ValidationError("Quotation must have a final version before accepting")

        lead: Lead = quotation.lead
        if not lead:
            raise NotFoundError("Lead", quotation.lead_id)

        # normalize for lookup only — store original in db
        normalized_name = lead.company_name.strip().lower()
        client = self.client_repository.get_by_company_name(db, normalized_name)
        if not client:
            client = self.client_repository.create(db, {
                "company_name": lead.company_name,
                "primary_contact_name": lead.contact_name,
                "primary_email": lead.email,
                "primary_phone": lead.phone,
            })

        project = self.project_repository.create(db, {
            "client_id": client.id,
            "status": "INITIATED",
        })

        updated_quotation = self.repository.update_quotation_status(db, quotation, "ACCEPTED")

        return {"quotation": updated_quotation, "project": project}