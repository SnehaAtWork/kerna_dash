# app/modules/clients/repositories.py

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.modules.clients.models import Client, Project


class ClientRepository:

    def get_by_company_name(self, db: Session, company_name: str) -> Client | None:
        # NOTE:
        # company_name lookup uses case-insensitive match via func.lower.
        # service layer normalizes input (strip + lower), but DB stores original.
        # proper long-term fix = store normalized column OR enforce constraint.
        stmt = select(Client).where(
            func.lower(Client.company_name) == company_name
        ).limit(1)
        return db.execute(stmt).scalars().first()

    def create(self, db: Session, data: dict) -> Client:
        client = Client(**data)
        db.add(client)
        db.flush()
        db.refresh(client)
        return client


class ProjectRepository:

    def create(self, db: Session, data: dict) -> Project:
        project = Project(**data)
        db.add(project)
        db.flush()
        db.refresh(project)
        return project

    def get_latest_by_client_id(self, db: Session, client_id) -> Project | None:
        stmt = (
            select(Project)
            .where(Project.client_id == client_id)
            .order_by(Project.created_at.desc())
            .limit(1)
        )
        return db.execute(stmt).scalars().first()
