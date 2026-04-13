import uuid

from sqlalchemy.orm import Session

from app.modules.project_modules.models import ModuleAssignment, ProjectModule
from app.modules.project_modules.repositories import ProjectModuleRepository
from app.shared.exceptions import NotFoundError, ValidationError

from app.shared.enums import MODULE_STATUSES


class ProjectModuleService:

    def __init__(self):
        self.repository = ProjectModuleRepository()

    def _get_module_or_raise(self, db: Session, module_id: uuid.UUID) -> ProjectModule:
        module = self.repository.get_module(db, module_id)
        if not module:
            raise NotFoundError("ProjectModule", module_id)
        return module

    def create_module(self, db: Session, project_id: uuid.UUID, data: dict) -> ProjectModule:
        if not project_id:
            raise ValidationError("project_id is required")
        # TODO: validate project existence via ProjectRepository
        if not data.get("module_type"):
            raise ValidationError("module_type is required")
        payload = {**data, "project_id": project_id, "status": MODULE_STATUSES[0]}
        return self.repository.create_module(db, payload)

    def list_modules(self, db: Session, project_id: uuid.UUID) -> list[ProjectModule]:
        return self.repository.list_by_project(db, project_id)

    def update_module_status(self, db: Session, module_id: uuid.UUID, status: str) -> ProjectModule:
        if not status:
            raise ValidationError("status is required")
        if status not in MODULE_STATUSES:
            raise ValidationError(f"Invalid module status. Allowed: {MODULE_STATUSES}")
        module = self._get_module_or_raise(db, module_id)
        return self.repository.update_module(db, module, {"status": status})

    def assign_user(self, db: Session, module_id: uuid.UUID, user_id: uuid.UUID) -> ModuleAssignment:
        if not user_id:
            raise ValidationError("user_id is required")
        self._get_module_or_raise(db, module_id)
        existing = self.repository.get_assignment(db, module_id, user_id)
        if existing:
            raise ValidationError("User already assigned to this module")
        return self.repository.assign_user(db, module_id, user_id)

    def unassign_user(self, db: Session, module_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self._get_module_or_raise(db, module_id)
        assignment = self.repository.get_assignment(db, module_id, user_id)
        if not assignment:
            raise NotFoundError("ModuleAssignment", f"{module_id}:{user_id}")
        self.repository.unassign_user(db, assignment)

    def list_assignments(self, db: Session, module_id: uuid.UUID) -> list[ModuleAssignment]:
        self._get_module_or_raise(db, module_id)
        return self.repository.get_assignments(db, module_id)