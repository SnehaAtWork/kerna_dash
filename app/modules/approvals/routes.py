# app/modules/approvals/routes.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.modules.approvals.services import ApprovalService

from app.modules.approvals.schemas import ApprovalAction

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("/versions/{version_id}/request")
def request_approval(
    version_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ApprovalService().request_approval(db, version_id, current_user)


@router.post("/{approval_id}/approve")
def approve(
    approval_id: UUID,
    data: ApprovalAction,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = data.user_id
    return ApprovalService().approve(db, approval_id, data.user_id, current_user)


@router.post("/{approval_id}/reject")
def reject(
    approval_id: UUID,
    data: ApprovalAction,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = data.user_id
    return ApprovalService().reject(db, approval_id, data.user_id, current_user)


@router.post("/{approval_id}/withdraw")
def withdraw(
    approval_id: UUID,
    data: ApprovalAction,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = data.user_id
    return ApprovalService().withdraw(db, approval_id, data.user_id, current_user)