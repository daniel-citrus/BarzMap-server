from fastapi import HTTPException
from pydantic import BaseModel, Field
from models.requests.ParkSubmissionRequest import ParkSubmissionRequest, ImageSubmission
from sqlalchemy.orm import Session
from services.Database import get_equipment
from services.Adapters.CloudflareAdapter import upload_images
from services.Database.ParksTable import create_park
from services.Database.ParkEquipmentTable import add_equipment_to_park
from services.Database.ImagesTable import create_image
from typing import List
from decimal import Decimal


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

        uploaded_images = None

        if submission.images and len(submission.images) <= 5:
            uploaded_images = await upload_images(submission.images)

        # Create park record in database
        park = create_park(
            db=db,
            name=submission.name,
            latitude=Decimal(str(submission.latitude)),
            longitude=Decimal(str(submission.longitude)),
            description=submission.description,
            address=submission.address,
            city=submission.city,
            state=submission.state,
            country=submission.country,
            postal_code=submission.postal_code,
            submitted_by=submission.submitted_by,
            status="pending",
        )
        
        # Link equipment to park
        if submission.equipment_ids:
            for equipment_id in submission.equipment_ids:
                add_equipment_to_park(
                    db=db,
                    park_id=park.id,
                    equipment_id=equipment_id,
                )
        
        # Link images to park
        if uploaded_images:
            for index, image in enumerate(uploaded_images):
                image_url = image.variants[0] if image.variants else None
                if not image_url:
                    continue
                
                create_image(
                    db=db,
                    park_id=park.id,
                    image_url=image_url,
                    uploaded_by=submission.submitted_by,
                    thumbnail_url=image.variants[-1] if image.variants and len(image.variants) > 1 else None,
                    is_primary=(index == 0),
                    is_approved=False,
                )
            
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
