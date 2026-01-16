from multiprocessing import process
import os
import asyncio
from dotenv import load_dotenv
from cloudflare import AsyncCloudflare
import logging
from typing import List
from models.requests.ParkSubmissionRequest import ParkSubmissionRequest, ImageSubmission
from services.Manager.ParkSubmissions import process_submission

# Load environment variables from .env file
load_dotenv()

client = AsyncCloudflare(api_token=os.environ.get("CLOUDFLARE_API_TOKEN"))
account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

logger = logging.getLogger(__name__)

sample_park_submission = ParkSubmissionRequest(
    name="Central Park Outdoor Gym",
    description="A great outdoor workout park with multiple exercise stations and beautiful scenery.",
    latitude=40.785091,
    longitude=-73.968285,
    address="Central Park, Upper East Side",
    city="New York",
    state="NY",
    country="USA",
    postal_code="10024",
    submitted_by=None,
    images=[
        ImageSubmission(
            file_data="",  # Placeholder - would be base64 encoded image data
            url="https://i.pinimg.com/736x/ff/35/01/ff3501402d2b46257e8d104508323a53.jpg",
            alt_text="Outdoor gym equipment at Central Park"
        ),
        ImageSubmission(
            file_data="",
            url="https://c4.wallpaperflare.com/wallpaper/635/923/784/anime-my-hero-academia-all-might-hd-wallpaper-preview.jpg",
            alt_text="Park overview"
        )
    ],
    equipment_ids=None
)

async def testParkSubmission(submission: ParkSubmissionRequest, image_urls: List):
    try:
        uploaded_images = []
        
        for url in image_urls:
            if url:
                uploaded_images.append(
                    await client.images.v1.create(
                        account_id=account_id,
                        url=url
                    )
                )

        submitted = process_submission(submission=submission)
        

    except Exception as e:
        logger.error(f"Something went wrong during image upload: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(testParkSubmission(sample_park_submission, image_urls))