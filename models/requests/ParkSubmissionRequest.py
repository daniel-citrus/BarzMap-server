from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from uuid import UUID


class ImageSubmission(BaseModel):
    """Image data for park submission."""
    file_data: str = Field(..., description="Image binary data")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alt text for accessibility")

class ParkSubmissionRequest(BaseModel):
    """Request model for submitting a new park with images."""
    # Park information
    name: str = Field(..., min_length=1, max_length=255, description="Name of the park")
    description: Optional[str] = Field(None, max_length=2000, description="Park description")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Full address display string")
    
    # Submission metadata
    submitted_by: Optional[UUID] = Field(None, description="User ID submitting the park")
    
    # Images (up to 5 as per business logic)
    images: Optional[List[ImageSubmission]] = Field(
        default=None,
        max_length=5,
        description="List of images to upload (maximum 5 images)"
    )
    
    # Equipment associated with the park
    equipment_ids: Optional[List[UUID]] = Field(
        default=None,
        description="List of equipment IDs available at this park"
    )
    
    @field_validator('images')
    @classmethod
    def validate_image_count(cls, v):
        """Ensure maximum of 5 images."""
        if v is not None and len(v) > 5:
            raise ValueError('Maximum of 5 images allowed per park submission')
        return v
    
    @field_validator('name', 'address')
    @classmethod
    def validate_string_fields(cls, v):
        """Strip whitespace from string fields."""
        if isinstance(v, str):
            return v.strip()
        return v

