from fastapi import HTTPException
from models.requests.ParkSubmissionRequest import ParkSubmissionRequest, ImageSubmission
from models.responses.ParkSubmissionResponse import ParkSubmissionResponse, ValidationResult
from sqlalchemy.orm import Session
from services.Database import get_equipment
from services.Adapters.CloudflareAdapter import upload_images
from services.Database.ParksTable import create_park
from services.Database.ParkEquipmentTable import add_equipment_to_park
from services.Database.ImagesTable import create_image
from decimal import Decimal


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


async def process_submission(submission: ParkSubmissionRequest, db: Session) -> ParkSubmissionResponse:
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
        images_uploaded_count = 0
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
                images_uploaded_count += 1
        

        return ParkSubmissionResponse(
            park_id=park.id,
            name=park.name,
            status=park.status,
            submitted_by=park.submitted_by,
            submit_date=park.submit_date,
            created_at=park.created_at,
            images_uploaded=images_uploaded_count,
            equipment_count=len(submission.equipment_ids) if submission.equipment_ids else 0,
        )

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
