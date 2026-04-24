from uuid import UUID
from pydantic import BaseModel


class ApprovalAction(BaseModel):
    user_id: UUID