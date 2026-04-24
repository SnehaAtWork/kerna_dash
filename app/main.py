from app.core.exceptions import register_exception_handlers
from fastapi import FastAPI
from dotenv import load_dotenv

import app.db.base  # noqa: F401 - import all models for Alembic
load_dotenv()

app = FastAPI()
register_exception_handlers(app)

# IMPORT ROUTERS
from app.modules.auth.routes import router as auth_router
from app.modules.leads.routes import router as leads_router
from app.modules.quotations.routes import router as quotations_router
from app.modules.project_modules.routes import router as modules_router
from app.modules.approvals.routes import router as approvals_router

# INCLUDE ROUTERS
app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(quotations_router)
app.include_router(modules_router)
app.include_router(approvals_router)