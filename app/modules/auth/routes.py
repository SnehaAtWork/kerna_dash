# app/modules/auth/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise HTTPException(status_code=422, detail="email and password required")
    return {
        "access_token": AuthService().login(db, email, password)
    }
