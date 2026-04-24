# app/modules/approvals/services.py

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.modules.project_modules.models import Approval
from app.modules.approvals.repositories import ApprovalRepository
from app.shared.exceptions import NotFoundError, ValidationError

APPROVAL_LOCK_HOURS = 48


class ApprovalService:

    def __init__(self):
        self.repository = ApprovalRepository()

    def _get_approval_or_raise(self, db: Session, approval_id: uuid.UUID) -> Approval:
        approval = self.repository.get_approval(db, approval_id)
        if not approval:
            raise NotFoundError("Approval", approval_id)
        return approval

    def _check_lock_not_expired(self, approval: Approval) -> None:
        if approval.lock_expires_at and datetime.now(timezone.utc) > approval.lock_expires_at:
            raise ValidationError("Approval window has expired")

    def request_approval(self, db: Session, module_version_id: uuid.UUID) -> Approval:
        version = self.repository.get_module_version(db, module_version_id)
        if not version:
            raise NotFoundError("ModuleVersion", module_version_id)
        existing = self.repository.get_by_version(db, module_version_id)
        if any(a.status == "PENDING" for a in existing):
            raise ValidationError("Pending approval already exists for this version")
        lock_expires_at = datetime.now(timezone.utc) + timedelta(hours=APPROVAL_LOCK_HOURS)
        return self.repository.create_approval(db, {
            "module_version_id": module_version_id,
            "status": "PENDING",
            "lock_expires_at": lock_expires_at,
        })

    def approve(self, db: Session, approval_id: uuid.UUID, user_id: uuid.UUID) -> Approval:
        if not user_id:
            raise ValidationError("user_id is required")
        approval = self._get_approval_or_raise(db, approval_id)
        if approval.status != "PENDING":
            raise ValidationError(f"Cannot approve: approval is {approval.status}")
        self._check_lock_not_expired(approval)
        with db.begin():
            return self.repository.update_approval(db, approval, {
                "status": "APPROVED",
                "approved_by": user_id,
                "approved_at": datetime.now(timezone.utc),
            })

    def reject(self, db: Session, approval_id: uuid.UUID, user_id: uuid.UUID) -> Approval:
        if not user_id:
            raise ValidationError("user_id is required")
        approval = self._get_approval_or_raise(db, approval_id)
        if approval.status != "PENDING":
            raise ValidationError(f"Cannot reject: approval is {approval.status}")
        self._check_lock_not_expired(approval)
        with db.begin():
            return self.repository.update_approval(db, approval, {
                "status": "REJECTED",
                "rejected_by": user_id,          # fixed: was approved_by
                "rejected_at": datetime.now(timezone.utc),  # fixed: was approved_at
            })

    def withdraw(self, db: Session, approval_id: uuid.UUID, user_id: uuid.UUID) -> Approval:
        if not user_id:
            raise ValidationError("user_id is required")
        approval = self._get_approval_or_raise(db, approval_id)
        if approval.status != "PENDING":
            raise ValidationError(f"Cannot withdraw: approval is {approval.status}")
        # lock window NOT checked on withdraw — user must always be able to withdraw while PENDING
        return self.repository.update_approval(db, approval, {
            "withdrawn_at": datetime.now(timezone.utc),
            "withdrawn_by": user_id,
        })
