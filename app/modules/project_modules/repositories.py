# app/modules/project_modules/repositories.py

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.project_modules.models import ModuleAssignment, ProjectModule


class ProjectModuleRepository:

    def create_module(self, db: Session, data: dict) -> ProjectModule:
        module = ProjectModule(**data)
        db.add(module)
        db.commit()
        db.refresh(module)
        return module

    def get_module(self, db: Session, module_id: uuid.UUID) -> ProjectModule | None:
        return db.get(ProjectModule, module_id)

    def list_by_project(self, db: Session, project_id: uuid.UUID) -> list[ProjectModule]:
        stmt = select(ProjectModule).where(ProjectModule.project_id == project_id)
        return db.execute(stmt).scalars().all()

    def update_module(self, db: Session, module: ProjectModule, data: dict) -> ProjectModule:
        for key, value in data.items():
            setattr(module, key, value)
        db.commit()
        db.refresh(module)
        return module

    def get_assignment(self, db: Session, module_id: uuid.UUID, user_id: uuid.UUID) -> ModuleAssignment | None:
        stmt = (
            select(ModuleAssignment)
            .where(
                ModuleAssignment.module_id == module_id,
                ModuleAssignment.user_id == user_id,
            )
            .limit(1)
        )
        return db.execute(stmt).scalars().first()

    def assign_user(self, db: Session, module_id: uuid.UUID, user_id: uuid.UUID) -> ModuleAssignment:
        assignment = ModuleAssignment(module_id=module_id, user_id=user_id)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def unassign_user(self, db: Session, assignment: ModuleAssignment) -> None:
        db.delete(assignment)
        db.commit()

    def get_assignments(self, db: Session, module_id: uuid.UUID) -> list[ModuleAssignment]:
        stmt = select(ModuleAssignment).where(ModuleAssignment.module_id == module_id)
        return db.execute(stmt).scalars().all()