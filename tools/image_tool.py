import logging
from google.genai import Client
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("nova.image")

IMAGE_API_KEY = os.getenv("GENAI_API_KEY_IMAGE")

image_client = Client(api_key=IMAGE_API_KEY)

def generate_image(prompt: str) -> str:
    """
    Generate an image from a text prompt and return the image URL.
    """
    logger.info(f"🖼️ Generating image for prompt: {prompt}")

    result = image_client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config={"number_of_images": 1}
    )

    image = result.generated_images[0]
    # image_url = image.image_uri

    logger.info("Image generated successfully")
    return {
        "type": "image",
        "url": image.image_uri,
        "prompt": prompt,
    }
