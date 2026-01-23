"""
Response models for park submission endpoints.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ValidationResult(BaseModel):
    """Result of park submission validation."""
    is_valid: bool = Field(..., description="Whether the submission passed validation")
    errors: List[str] = Field(default_factory=list, description="List of validation error messages")


class ParkSubmissionResponse(BaseModel):
    """Response model for park submission processing."""
    park_id: UUID = Field(..., description="ID of the created park")
    name: str = Field(..., description="Name of the park")
    status: str = Field(..., description="Status of the park (pending, approved, rejected)")
    submitted_by: Optional[UUID] = Field(None, description="User who submitted the park")
    submit_date: datetime = Field(..., description="When the park was submitted")
    created_at: datetime = Field(..., description="When the park record was created")
    images_uploaded: int = Field(..., description="Number of images successfully uploaded")
    equipment_count: int = Field(..., description="Number of equipment items linked to the park")
    
    model_config = ConfigDict(from_attributes=True)

