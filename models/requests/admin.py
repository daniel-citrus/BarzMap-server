from pydantic import BaseModel
from typing import Optional, Literal


class ModerationComment(BaseModel):
    """Request body for moderation actions (legacy)."""
    comment: Optional[str] = ""


class ModerateParkSubmissionRequest(BaseModel):
    """Request body for PATCH park submission (moderation)."""
    status: Literal["approved", "rejected", "pending"]
    comment: Optional[str] = ""
