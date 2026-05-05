# app/modules/quotations/services.py

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.clients.models import Client, Project
from app.modules.clients.repositories import ClientRepository, ProjectRepository
from app.modules.leads.models import Lead
from app.modules.leads.services import QUALIFIED_STATES
from app.modules.quotations.models import Quotation, QuotationLineItem, QuotationVersion
from app.modules.quotations.repositories import QuotationRepository
from app.shared.exceptions import NotFoundError, ValidationError

QUOTATION_TRANSITIONS: dict[str, list[str]] = {
    "DRAFT":               ["READY_FOR_SUBMISSION", "SUBMITTED"],
    "READY_FOR_SUBMISSION": ["SUBMITTED"],
    "SUBMITTED":           ["VIEWED", "AWAITING_RESPONSE", "REVISION_REQUESTED", "REJECTED"],
    "VIEWED":              ["AWAITING_RESPONSE", "REVISION_REQUESTED", "REJECTED"],
    "AWAITING_RESPONSE":   ["NEGOTIATION", "REVISION_REQUESTED", "APPROVED", "REJECTED"],
    "NEGOTIATION":         ["REVISION_REQUESTED", "APPROVED", "REJECTED"],
    "REVISION_REQUESTED":  ["DRAFT"],
    "APPROVED":            ["CONVERTED"],
    "REJECTED":            [],
    "CONVERTED":           [],
}

LOCKED_STATES = {
    "SUBMITTED", "VIEWED", "AWAITING_RESPONSE",
    "NEGOTIATION", "APPROVED", "CONVERTED", "REJECTED",
}


def _assert_transition(quotation: Quotation, target: str) -> None:
    allowed = QUOTATION_TRANSITIONS.get(quotation.status, [])
    if target not in allowed:
        raise ValidationError(
            f"Cannot transition quotation from {quotation.status} to {target}. "
            f"Allowed: {allowed or 'none (terminal state)'}"
        )


def _assert_editable(quotation: Quotation) -> None:
    if quotation.status in LOCKED_STATES:
        raise ValidationError(
            f"Quotation is locked in state {quotation.status}. "
            "No further edits allowed."
        )


class QuotationService:

    def __init__(self):
        self.repository = QuotationRepository()
        self.client_repository = ClientRepository()
        self.project_repository = ProjectRepository()

    def list_quotations(self, db: Session, lead_id: uuid.UUID | None = None) -> list[Quotation]:
        return self.repository.list_all(db, lead_id)

    def create_quotation(self, db: Session, lead_id: uuid.UUID, data: dict) -> Quotation:
        if not lead_id:
            raise ValidationError("lead_id is required")
        lead: Lead | None = db.get(Lead, lead_id)
        if not lead:
            raise NotFoundError("Lead", lead_id)
        if lead.status not in QUALIFIED_STATES:
            raise ValidationError(
                f"Quotation can only be created for qualified leads. "
                f"Lead is currently {lead.status}."
            )
        payload = {**data, "lead_id": lead_id, "status": "DRAFT"}
        payload.pop("status_override", None)
        return self.repository.create_quotation(db, payload)

    def get_quotation(self, db: Session, quotation_id: uuid.UUID) -> Quotation:
        quotation = self.repository.get_quotation(db, quotation_id)
        if not quotation:
            raise NotFoundError("Quotation", quotation_id)
        return quotation

    def add_version(self, db: Session, quotation_id: uuid.UUID, data: dict) -> QuotationVersion:
        quotation = self.get_quotation(db, quotation_id)
        _assert_editable(quotation)
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
        quotation = self.get_quotation(db, version.quotation_id)
        _assert_editable(quotation)
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
        result = self.repository.set_version_final(db, version)
        db.commit()
        return result

    def submit_quotation(self, db: Session, quotation_id: uuid.UUID) -> Quotation:
        quotation = self.get_quotation(db, quotation_id)
        _assert_transition(quotation, "SUBMITTED")
        latest = self.repository.get_latest_version(db, quotation_id)
        if not latest:
            raise ValidationError("Quotation must have at least one version before submission")
        line_items = self.repository.get_line_items_for_version(db, latest.id)
        if not line_items:
            raise ValidationError("Quotation version must have at least one line item before submission")
        return self.repository.update_quotation_status(db, quotation, "SUBMITTED")

    def mark_viewed(self, db: Session, quotation_id: uuid.UUID) -> Quotation:
        quotation = self.get_quotation(db, quotation_id)
        _assert_transition(quotation, "VIEWED")
        return self.repository.update_quotation_status(db, quotation, "VIEWED")

    def mark_awaiting_response(self, db: Session, quotation_id: uuid.UUID) -> Quotation:
        quotation = self.get_quotation(db, quotation_id)
        _assert_transition(quotation, "AWAITING_RESPONSE")
        return self.repository.update_quotation_status(db, quotation, "AWAITING_RESPONSE")

    def mark_negotiation(self, db: Session, quotation_id: uuid.UUID) -> Quotation:
        quotation = self.get_quotation(db, quotation_id)
        _assert_transition(quotation, "NEGOTIATION")
        return self.repository.update_quotation_status(db, quotation, "NEGOTIATION")

    def approve_quotation(self, db: Session, quotation_id: uuid.UUID, feedback: str | None = None) -> Quotation:
        quotation = self.get_quotation(db, quotation_id)
        _assert_transition(quotation, "APPROVED")
        if feedback:
            self.repository.update_quotation_notes(db, quotation, feedback)
        return self.repository.update_quotation_status(db, quotation, "APPROVED")

    def reject_quotation(self, db: Session, quotation_id: uuid.UUID, reason: str) -> Quotation:
        if not reason or not reason.strip():
            raise ValidationError("Rejection reason is required")
        quotation = self.get_quotation(db, quotation_id)
        _assert_transition(quotation, "REJECTED")
        self.repository.update_quotation_notes(db, quotation, reason)
        return self.repository.update_quotation_status(db, quotation, "REJECTED")

    def create_revision(self, db: Session, quotation_id: uuid.UUID, feedback: str | None = None) -> QuotationVersion:
        quotation = self.get_quotation(db, quotation_id)
        _assert_transition(quotation, "DRAFT")
        latest = self.repository.get_latest_version(db, quotation_id)
        next_number = (latest.version_number + 1) if latest else 1
        payload = {
            "quotation_id": quotation_id,
            "version_number": next_number,
            "is_final": False,
            "subtotal": 0,
            "discount": 0,
            "total": 0,
            "notes": feedback,
        }
        new_version = self.repository.create_version(db, payload)
        self.repository.update_quotation_status(db, quotation, "DRAFT")
        return new_version

    def convert_quotation(self, db: Session, quotation_id: uuid.UUID) -> dict:
        quotation = self.get_quotation(db, quotation_id)
        _assert_transition(quotation, "CONVERTED")

        lead: Lead = quotation.lead
        if not lead:
            raise NotFoundError("Lead", quotation.lead_id)

        normalized_name = lead.company_name.strip().lower()
        client = self.client_repository.get_by_company_name(db, normalized_name)
        if not client:
            client = self.client_repository.create(db, {
                "company_name": lead.company_name,
                "primary_contact_name": lead.contact_name or "",
                "primary_email": lead.email or "",
                "primary_phone": lead.phone,
            })

        project = self.project_repository.create(db, {
            "client_id": client.id,
            "status": "INITIATED",
            "quotation_id": quotation_id,
        })

        updated_quotation = self.repository.update_quotation_status(db, quotation, "CONVERTED")
        return {"quotation": updated_quotation, "project": project}

    def accept_quotation(self, db: Session, quotation_id: uuid.UUID, current_user) -> dict:
        """Legacy endpoint — delegates to convert_quotation after approval check."""
        quotation = self.get_quotation(db, quotation_id)

        if quotation.status == "CONVERTED":
            lead: Lead = quotation.lead
            existing_client = self.client_repository.get_by_company_name(
                db, lead.company_name.strip().lower()
            ) if lead else None
            existing_project = (
                self.project_repository.get_latest_by_client_id(db, existing_client.id)
                if existing_client else None
            )
            return {"quotation": quotation, "project": existing_project}

        if quotation.status != "APPROVED":
            raise ValidationError(
                "Quotation must be Approved before converting. "
                "Use POST /quotations/{id}/approve first."
            )

        return self.convert_quotation(db, quotation_id)
