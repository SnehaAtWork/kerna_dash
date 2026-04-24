# app/modules/quotations/repositories.py

import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.quotations.models import Quotation, QuotationLineItem, QuotationVersion


class QuotationRepository:

    def create_quotation(self, db: Session, data: dict) -> Quotation:
        quotation = Quotation(**data)
        db.add(quotation)
        db.flush()
        db.commit()
        db.refresh(quotation)
        return quotation

    def get_quotation(self, db: Session, quotation_id: uuid.UUID) -> Quotation | None:
        return db.get(Quotation, quotation_id)

    def create_version(self, db: Session, data: dict) -> QuotationVersion:
        version = QuotationVersion(**data)
        db.add(version)
        db.flush()
        db.commit()
        db.refresh(version)
        return version

    def get_versions(self, db: Session, quotation_id: uuid.UUID) -> list[QuotationVersion]:
        stmt = (
            select(QuotationVersion)
            .where(QuotationVersion.quotation_id == quotation_id)
            .order_by(QuotationVersion.version_number)
        )
        return db.execute(stmt).scalars().all()

    def get_latest_version(self, db: Session, quotation_id: uuid.UUID) -> QuotationVersion | None:
        stmt = (
            select(QuotationVersion)
            .where(QuotationVersion.quotation_id == quotation_id)
            .order_by(QuotationVersion.version_number.desc())
            .limit(1)
        )
        return db.execute(stmt).scalars().first()

    def get_final_version(self, db: Session, quotation_id: uuid.UUID) -> QuotationVersion | None:
        stmt = (
            select(QuotationVersion)
            .where(
                QuotationVersion.quotation_id == quotation_id,
                QuotationVersion.is_final == True,
            )
            .limit(1)
        )
        return db.execute(stmt).scalars().first()

    def get_version(self, db: Session, version_id: uuid.UUID) -> QuotationVersion | None:
        return db.get(QuotationVersion, version_id)

    def create_line_items(self, db: Session, version_id: uuid.UUID, items: list[dict]) -> list[QuotationLineItem]:
        line_items = [
            QuotationLineItem(quotation_version_id=version_id, **item)
            for item in items
        ]
        db.add_all(line_items)
        db.flush()
        for item in line_items:
            db.commit()
            db.refresh(item)
        return line_items

    def unset_final_versions(self, db: Session, quotation_id: uuid.UUID) -> None:
        stmt = (
            update(QuotationVersion)
            .where(QuotationVersion.quotation_id == quotation_id)
            .values(is_final=False)
        )
        db.execute(stmt)

    def set_version_final(self, db: Session, version: QuotationVersion) -> QuotationVersion:
        version.is_final = True
        db.flush()
        db.commit()
        db.refresh(version)
        return version

    def update_quotation_status(self, db: Session, quotation: Quotation, status: str) -> Quotation:
        quotation.status = status
        db.flush()
        db.commit()
        db.refresh(quotation)
        return quotation
