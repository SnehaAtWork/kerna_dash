# app/modules/auth/service.py

from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.core.exceptions import ValidationError
from app.modules.users.repositories import UserRepository


class AuthService:

    def login(self, db: Session, email: str, password: str) -> str:
        user = UserRepository().get_by_email(db, email)
        if not user:
            raise ValidationError("Invalid credentials")
        if user.password_hash != password:
            raise ValidationError("Invalid credentials")
        return create_access_token(str(user.id))
