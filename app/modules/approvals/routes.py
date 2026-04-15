# app/modules/approvals/routes.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.approvals.services import ApprovalService

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("/versions/{version_id}/request")
def request_approval(version_id: UUID, db: Session = Depends(get_db)):
    return ApprovalService().request_approval(db, version_id)


@router.post("/{approval_id}/approve")
def approve(approval_id: UUID, data: dict, db: Session = Depends(get_db)):
    try:
        user_id = UUID(str(data.get("user_id")))
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid user_id")
    return ApprovalService().approve(db, approval_id, user_id)


@router.post("/{approval_id}/reject")
def reject(approval_id: UUID, data: dict, db: Session = Depends(get_db)):
    try:
        user_id = UUID(str(data.get("user_id")))
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid user_id")
    return ApprovalService().reject(db, approval_id, user_id)


@router.post("/{approval_id}/withdraw")
def withdraw(approval_id: UUID, data: dict, db: Session = Depends(get_db)):
    try:
        user_id = UUID(str(data.get("user_id")))
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid user_id")
    return ApprovalService().withdraw(db, approval_id, user_id)