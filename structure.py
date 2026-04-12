import os

structure = {
    "alembic/env.py": "",
    "alembic.ini": "",
    "requirements.txt": "",
    "tests/__init__.py": "",
    "tests/unit/__init__.py": "",
    "tests/integration/__init__.py": "",
    "app/__init__.py": "",
    "app/main.py": "",
    "app/ARCHITECTURE_RULES.md": "",
    "app/api/__init__.py": "",
    "app/api/router.py": "",
    "app/audit/__init__.py": "",
    "app/audit/models.py": "",
    "app/audit/repositories.py": "",
    "app/audit/routes.py": "",
    "app/audit/schemas.py": "",
    "app/audit/services.py": "",
    "app/core/__init__.py": "",
    "app/core/config.py": "",
    "app/core/database.py": "",
    "app/core/dependencies.py": "",
    "app/core/security.py": "",
    "app/events/__init__.py": "",
    "app/events/dispatcher.py": "",
    "app/events/handlers/__init__.py": "",
    "app/events/handlers/approval_handlers.py": "",
    "app/events/handlers/escalation_handlers.py": "",
    "app/events/handlers/payment_handlers.py": "",
    "app/notifications/__init__.py": "",
    "app/notifications/models.py": "",
    "app/notifications/repositories.py": "",
    "app/notifications/routes.py": "",
    "app/notifications/schemas.py": "",
    "app/notifications/services.py": "",
    "app/shared/__init__.py": "",
    "app/shared/base.py": "",
    "app/shared/enums.py": "",
    "app/shared/exceptions.py": "",
    "app/shared/utils.py": "",
}

modules = [
    "approvals", "auth", "clients", "contracts", "credentials",
    "escalations", "invoices", "leads", "milestones", "payments",
    "project_modules", "projects", "quotations", "subscriptions",
    "users", "vault"
]

for module in modules:
    base = f"app/modules/{module}"
    files = ["__init__.py", "models.py", "repositories.py", "routes.py", "schemas.py", "services.py"]
    
    if module == "credentials":
        files = [
            "__init__.py",
            "models_access_methods.py",
            "models_access_sessions.py",
            "models_api_logs.py",
            "repositories.py",
            "routes.py",
            "schemas.py",
            "services.py"
        ]
    
    for f in files:
        structure[f"{base}/{f}"] = ""

# create files
for path in structure:
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w") as f:
        f.write("")

print("done")