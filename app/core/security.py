# app/core/security.py

from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "kerna-secret-change-in-prod"
ALGORITHM = "HS256"
EXPIRY_MINUTES = 60


def create_access_token(user_id: str) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=EXPIRY_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    # raises JWTError if invalid/expired
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
