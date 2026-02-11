from fastapi import HTTPException
from fastapi.datastructures import UploadFile
from models.requests.ParkSubmissionRequest import ParkSubmissionRequest, ImageSubmission
from models.responses.ParkSubmissionResponse import ParkSubmissionResponse, ValidationResult
from sqlalchemy.orm import Session
from services.Database import get_equipment
from models.responses.CloudflareImageResponses import UploadedImage
from services.Adapters.CloudflareAdapter import upload_images
from services.Database.ParksTable import create_park
from services.Database.ParkEquipmentTable import add_equipment_to_park
from services.Database.ImagesTable import create_image
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
import json
import logging

logger = logging.getLogger(__name__)


async def parse_submission_form_data(
    name: str,
    description: Optional[str],
    latitude: float,
    longitude: float,
    address: Optional[str],
    submitted_by: Optional[str],
    equipment_ids: Optional[str],
    images: Optional[List[UploadFile]],
    image_alt_texts: Optional[str],
) -> ParkSubmissionRequest:
    """
    Parse and validate multipart form data into a ParkSubmissionRequest.
    
    Handles:
    - Image count validation
    - JSON parsing for equipment_ids and image_alt_texts
    - UUID parsing for submitted_by
    - Reading file contents from UploadFile objects
    - Creating ImageSubmission objects
    """
    # Handle None or empty images
    images_list = images if images else []
    
    # Validate image count
    if len(images_list) > 5:
        raise HTTPException(status_code=400, detail="Maximum of 5 images allowed per park submission")
    
    # Parse equipment_ids if provided
    equipment_ids_list = None
    if equipment_ids:
        try:
            equipment_ids_list = json.loads(equipment_ids)
            if not isinstance(equipment_ids_list, list):
                raise ValueError("equipment_ids must be a JSON array")
            equipment_ids_list = [UUID(eid) for eid in equipment_ids_list]
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid equipment_ids format: {str(e)}")
    
    # Parse submitted_by if provided
    submitted_by_uuid = None
    if submitted_by:
        try:
            submitted_by_uuid = UUID(submitted_by)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid submitted_by UUID format")
    
    # Parse image alt texts if provided
    alt_texts_list = []
    if image_alt_texts:
        try:
            alt_texts_list = json.loads(image_alt_texts)
            if not isinstance(alt_texts_list, list):
                raise ValueError("image_alt_texts must be a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid image_alt_texts format: {str(e)}")
    
    # Process images - read file data and create ImageSubmission objects
    image_submissions = []
    if images_list:
        for idx, image_file in enumerate(images_list):
            file_content = await image_file.read()
            alt_text = alt_texts_list[idx] if idx < len(alt_texts_list) else None
            image_submissions.append(ImageSubmission(
                file_data=file_content,
                alt_text=alt_text
            ))
    
    # Create and return ParkSubmissionRequest
    return ParkSubmissionRequest(
        name=name.strip() if name else name,
        description=description,
        latitude=latitude,
        longitude=longitude,
        address=address.strip() if address else address,
        submitted_by=submitted_by_uuid,
        equipment_ids=equipment_ids_list,
        images=image_submissions if image_submissions else None
    )


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

        if submission.images and len(submission.images) > 0:
            if len(submission.images) > 5:
                logger.warning(f"Too many images provided ({len(submission.images)}), only uploading first 5")
                submission.images = submission.images[:5]
            
            try:
                uploaded_images = await upload_images(submission.images)
            except HTTPException:
                # Re-raise HTTPExceptions (e.g., all uploads failed)
                raise
            except Exception as e:
                logger.error(f"Failed to upload images to Cloudflare: {str(e)}", exc_info=True)
                # Continue with park creation even if image upload fails
                uploaded_images = None

        # Create park record in database
        park = create_park(
            db=db,
            name=submission.name,
            latitude=Decimal(str(submission.latitude)),
            longitude=Decimal(str(submission.longitude)),
            description=submission.description,
            address=submission.address,
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
                
                try:
                    created_image = create_image(
                        db=db,
                        park_id=park.id,
                        image_url=image_url,
                        uploaded_by=submission.submitted_by,
                        thumbnail_url=image.variants[-1] if image.variants and len(image.variants) > 1 else None,
                        is_primary=(index == 0),
                        is_approved=False,
                    )
                    # Verify creation was successful
                    if created_image and created_image.id:
                        images_uploaded_count += 1
                    else:
                        logger.warning(f"Image creation returned None or invalid image for index {index}")
                except Exception as e:
                    logger.error(f"Failed to create image at index {index}: {str(e)}", exc_info=True)
                    # Continue processing other images even if one fails
        

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
