"""
Main API router for park submissions.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.requests.ParkSubmissionRequest import ParkSubmissionRequest
from services.Manager.ParkSubmissions import process_submission
from services.Database import get_db

router = APIRouter()


class ParkSubmissionResponse(BaseModel):
    """Response model for park submission."""
    message: str
    submitted: bool


@router.post("/submit", response_model=ParkSubmissionResponse, tags=["Submissions"])
async def submit_park(
    submission: ParkSubmissionRequest,
    db: Session = Depends(get_db)
) -> ParkSubmissionResponse:
    """Submit a new park with images and equipment."""
    await process_submission(submission, db)
    return ParkSubmissionResponse(
        message="Park submission processed successfully",
        submitted=True
    )

