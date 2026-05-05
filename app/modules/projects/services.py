# app/modules/projects/services.py

import uuid

from sqlalchemy.orm import Session

from app.modules.clients.models import Project
from app.modules.projects.repositories import ProjectRepository
from app.shared.exceptions import NotFoundError


class ProjectService:

    def __init__(self):
        self.repository = ProjectRepository()

    def list_projects(self, db: Session) -> list[Project]:
        return self.repository.list_all(db)

    def get_project(self, db: Session, project_id: uuid.UUID) -> Project:
        project = self.repository.get_by_id(db, project_id)
        if not project:
            raise NotFoundError("Project", project_id)
        return project
