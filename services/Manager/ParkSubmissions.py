from fastapi import HTTPException
from pydantic import BaseModel, Field
from models.requests.ParkSubmissionRequest import ParkSubmissionRequest, ImageSubmission
from sqlalchemy.orm import Session
from services.Database import get_equipment
from services.Adapters.CloudflareAdapter import upload_images
from services.Database.ParksTable import create_park
from typing import List


class ValidationResult(BaseModel):
    """Result of park submission validation."""
    is_valid: bool = Field(..., description="Whether the submission passed validation")
    errors: List[str] = Field(default_factory=list, description="List of validation error messages")


def validate_submission(
    submission: ParkSubmissionRequest, db: Session
) -> ValidationResult:
    """
    Validate park submission business logic.
    """
    errors = []

    # Validate equipment IDs exist in database using try/except error handling
    if submission.equipment_ids:
        for equipment_id in submission.equipment_ids:
            try:
                equipment = get_equipment(db, equipment_id)

                if not equipment:
                    raise ValueError(f"Equipment with ID {equipment_id} does not exist")
            except ValueError as e:
                errors.append(str(e))
            except Exception as e:
                errors.append(f"Error validating equipment ID {equipment_id}: {str(e)}")

    # Add more business logic validations here as needed:
    # - Check for duplicate parks at same location
    # - Validate user permissions
    # - Check image format/size limits
    # etc.

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )


async def process_submission(submission: ParkSubmissionRequest, db: Session):
    try:
        validation_result = validate_submission(submission, db)

        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Park submission validation failed",
                    "errors": validation_result.errors,
                },
            )

        if submission.images and len(submission.images) <= 5:
            uploaded_images = await upload_images(submission.images)

        # TODO: Create park record in database

        # TODO: Link equipment to park
        # TODO: Return created park data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An unexpected error occurred while processing park submission",
                "error": str(e),
            },
        )
