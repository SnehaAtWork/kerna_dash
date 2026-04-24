# app/modules/project_modules/routes.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.modules.project_modules.services import ProjectModuleService

from app.modules.project_modules.schemas import (
    ModuleCreate,
    ModuleStatusUpdate,
    ModuleAssign,
)

router = APIRouter(tags=["Project Modules"])


@router.post("/projects/{project_id}/modules")
def create_module(project_id: UUID, data: ModuleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user),):
    return ProjectModuleService().create_module(db, project_id, data.dict(), current_user)


@router.get("/projects/{project_id}/modules")
def list_modules(project_id: UUID, db: Session = Depends(get_db)):
    return ProjectModuleService().list_modules(db, project_id)


@router.patch("/{module_id}/status")
def update_module_status(module_id: UUID, data: ModuleStatusUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user),):
    return ProjectModuleService().update_module_status(db, module_id, data.status, current_user)


@router.post("/{module_id}/assign")
def assign_user(module_id: UUID, data: ModuleAssign, db: Session = Depends(get_db), current_user=Depends(get_current_user),):
    user_id = data.user_id
    return ProjectModuleService().assign_user(db, module_id, data.user_id, current_user)


@router.delete("/{module_id}/assign")
def unassign_user(
    module_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ProjectModuleService().unassign_user(db, module_id, user_id, current_user)


@router.get("/{module_id}/assignments")
def list_assignments(module_id: UUID, db: Session = Depends(get_db)):
    return ProjectModuleService().list_assignments(db, module_id)