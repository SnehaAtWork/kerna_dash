# app/modules/approvals/repositories.py

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.project_modules.models import Approval, ModuleVersion


class ApprovalRepository:

    def create_approval(self, db: Session, data: dict) -> Approval:
        approval = Approval(**data)
        db.add(approval)
        db.flush()
        db.refresh(approval)
        return approval

    def get_approval(self, db: Session, approval_id: uuid.UUID) -> Approval | None:
        return db.get(Approval, approval_id)

    def get_by_version(self, db: Session, module_version_id: uuid.UUID) -> list[Approval]:
        stmt = select(Approval).where(Approval.module_version_id == module_version_id)
        return db.execute(stmt).scalars().all()

    def get_module_version(self, db: Session, module_version_id: uuid.UUID) -> ModuleVersion | None:
        return db.get(ModuleVersion, module_version_id)

    def update_approval(self, db: Session, approval: Approval, data: dict) -> Approval:
        for key, value in data.items():
            setattr(approval, key, value)
        db.flush()
        db.refresh(approval)
        return approval
