from pydantic import BaseModel
from typing import Optional


class ModerationComment(BaseModel):
    """Request body for moderation actions."""
    comment: Optional[str] = ""
