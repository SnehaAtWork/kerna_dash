# app/modules/auth/service.py

import logging

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.core.exceptions import ValidationError
from app.modules.users.repositories import UserRepository

logger = logging.getLogger(__name__)


class AuthService:

    def login(self, db: Session, email: str, password: str) -> str:
        user = UserRepository().get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise ValidationError("Invalid credentials")
        if not user.active:
            raise ValidationError("Invalid credentials")
        logger.info(f"User login: {user.id}")
        return create_access_token(str(user.id))