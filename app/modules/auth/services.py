# app/modules/auth/service.py

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.core.exceptions import ValidationError
from app.modules.users.repositories import UserRepository

logger = logging.getLogger(__name__)


class AuthService:

    def login(self, db: Session, email: str, password: str) -> tuple:
        user = UserRepository().get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise ValidationError("Invalid credentials")
        if not user.active:
            raise ValidationError("Invalid credentials")
        logger.info(f"User login: {user.id}")
        return user, create_access_token(str(user.id))

    def request_password_reset(self, db: Session, email: str) -> str | None:
        user = UserRepository().get_by_email(db, email)
        if not user or not user.active:
            return None
        token = create_password_reset_token(str(user.id))
        user.reset_token_hash = hash_token(token)
        user.reset_token_expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        db.commit()
        logger.info(f"Password reset requested for user: {user.id}")
        return token

    def reset_password(self, db: Session, token: str, new_password: str) -> None:
        try:
            user_id_str = decode_password_reset_token(token)
            user_id = UUID(user_id_str)
        except Exception:
            raise ValidationError("Invalid or expired reset token")

        user = UserRepository().get_by_id(db, user_id)
        if not user:
            raise ValidationError("Invalid or expired reset token")

        if not user.reset_token_hash or user.reset_token_hash != hash_token(token):
            raise ValidationError("Invalid or expired reset token")

        user.password_hash = hash_password(new_password)
        user.reset_token_hash = None
        user.reset_token_expires_at = None
        db.commit()
        logger.info(f"Password reset completed for user: {user.id}")
