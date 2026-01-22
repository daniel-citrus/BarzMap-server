"""
Main API router for park submissions.
"""
from fastapi import APIRouter, Depends, Body
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
    submission: ParkSubmissionRequest = Body(
        ...,
        example={
            "name": "Central Park Outdoor Gym",
            "description": "A great outdoor workout park with multiple exercise stations and beautiful scenery.",
            "latitude": 40.785091,
            "longitude": -73.968285,
            "address": "Central Park, Upper East Side",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10024",
            "submitted_by": None,
            "images": [
                {
                    "file_data": "",
                    "url": "https://i.pinimg.com/736x/ff/35/01/ff3501402d2b46257e8d104508323a53.jpg",
                    "alt_text": "Outdoor gym equipment at Central Park"
                },
                {
                    "file_data": "",
                    "url": "https://c4.wallpaperflare.com/wallpaper/635/923/784/anime-my-hero-academia-all-might-hd-wallpaper-preview.jpg",
                    "alt_text": "Park overview"
                },
                {
                    "file_data": "",
                    "url": "https://c4.wallpaperflare.com/wallpaper/635/923/784/anime-my-hero-academia-all-might-hd-wallpaper-preview.jpg",
                    "alt_text": "Park overvie2"
                }
            ],
            "equipment_ids": None
        }
    ),
    db: Session = Depends(get_db)
) -> ParkSubmissionResponse:
    """Submit a new park with images and equipment."""
    await process_submission(submission, db)
    
    return ParkSubmissionResponse(
        message="Park submission processed successfully",
        submitted=True
    )

