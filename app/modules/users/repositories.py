from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import func

from app.modules.users.models import User


class UserRepository:

    def get_by_email(self, db: Session, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.lower())
        return db.execute(stmt).scalars().first()

    def get_by_id(self, db: Session, user_id) -> User | None:
        return db.get(User, user_id)