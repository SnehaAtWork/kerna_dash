# app/modules/projects/repositories.py

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.clients.models import Project


class ProjectRepository:

    def list_all(self, db: Session) -> list[Project]:
        stmt = select(Project).order_by(Project.created_at.desc())
        return db.execute(stmt).scalars().all()

    def get_by_id(self, db: Session, project_id: uuid.UUID) -> Project | None:
        return db.get(Project, project_id)
