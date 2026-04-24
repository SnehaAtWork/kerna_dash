# app/core/permissions.py

def has_permission(user, permission: str) -> bool:
    if not user or not getattr(user, "role", None):
        return False
    if getattr(user.role, "name", None) == "ADMIN":
        return True
    return permission in getattr(user.role, "permissions", [])