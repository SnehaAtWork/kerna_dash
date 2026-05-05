# app/modules/auth/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.modules.auth.services import AuthService
from app.shared.exceptions import ValidationError

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(status_code=422, detail="email and password required")

    try:
        user, token = AuthService().login(db, email, password)
    except ValidationError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "roles": [r.name for r in user.roles],
        },
    }


@router.post("/forgot-password")
def forgot_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=422, detail="email required")

    token = AuthService().request_password_reset(db, email)

    response: dict = {"message": "If an account exists for this email, you'll receive reset instructions shortly."}
    if token:
        # In production this would be sent via email. Returned here for dev/testing.
        response["reset_token"] = token
    return response


@router.post("/reset-password")
def reset_password(data: dict, db: Session = Depends(get_db)):
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        raise HTTPException(status_code=422, detail="token and new_password required")

    try:
        AuthService().reset_password(db, token, new_password)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Password reset successful"}


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "roles": [r.name for r in current_user.roles],
    }
