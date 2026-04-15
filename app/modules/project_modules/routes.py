# app/modules/project_modules/routes.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.project_modules.services import ProjectModuleService

router = APIRouter(tags=["Project Modules"])


@router.post("/projects/{project_id}/modules")
def create_module(project_id: UUID, data: dict, db: Session = Depends(get_db)):
    return ProjectModuleService().create_module(db, project_id, data)


@router.get("/projects/{project_id}/modules")
def list_modules(project_id: UUID, db: Session = Depends(get_db)):
    return ProjectModuleService().list_modules(db, project_id)


@router.patch("/{module_id}/status")
def update_module_status(module_id: UUID, data: dict, db: Session = Depends(get_db)):
    status = data.get("status")
    if not isinstance(status, str):
        raise HTTPException(status_code=422, detail="status must be string")
    return ProjectModuleService().update_module_status(db, module_id, status)


@router.post("/{module_id}/assign")
def assign_user(module_id: UUID, data: dict, db: Session = Depends(get_db)):
    try:
        user_id = UUID(str(data.get("user_id")))
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid user_id")
    return ProjectModuleService().assign_user(db, module_id, user_id)


@router.delete("/{module_id}/assign")
def unassign_user(
    module_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return ProjectModuleService().unassign_user(db, module_id, user_id)


@router.get("/{module_id}/assignments")
def list_assignments(module_id: UUID, db: Session = Depends(get_db)):
    return ProjectModuleService().list_assignments(db, module_id)