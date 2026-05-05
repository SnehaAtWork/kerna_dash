# app/modules/projects/routes.py

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.modules.projects.services import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/")
def list_projects(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return ProjectService().list_projects(db)


@router.get("/{project_id}")
def get_project(project_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return ProjectService().get_project(db, project_id)
