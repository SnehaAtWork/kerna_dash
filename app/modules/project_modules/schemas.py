from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class ModuleCreate(BaseModel):
    module_type: str


class ModuleStatusUpdate(BaseModel):
    status: str


class ModuleAssign(BaseModel):
    user_id: UUID