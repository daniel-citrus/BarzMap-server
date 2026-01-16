import os
import asyncio
from dotenv import load_dotenv
from cloudflare import AsyncCloudflare
import logging
from typing import List

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

image_urls = [
    "https://i.pinimg.com/736x/ff/35/01/ff3501402d2b46257e8d104508323a53.jpg",
    "",
    "https://c4.wallpaperflare.com/wallpaper/635/923/784/anime-my-hero-academia-all-might-hd-wallpaper-preview.jpg"
]


async def testParkSubmission(image_urls: List):
    try:
        client = AsyncCloudflare(
            api_token=os.environ.get("CLOUDFLARE_API_TOKEN"),
        )

        account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

        uploaded_images = []
        
        for url in image_urls:
            if url:
                uploaded_images.append(
                    await client.images.v1.create(
                        account_id=account_id,
                        url=url
                    )
                )

        print(uploaded_images)
    except Exception as e:
        logger.error(f"Something went wrong during image upload: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(testParkSubmission(image_urls))