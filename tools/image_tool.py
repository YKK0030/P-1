import logging
from google.genai import Client
from google.genai.errors import ClientError, APIError
import os
from dotenv import load_dotenv
from config.config import APIKeyRotator
from config.logger import get_logger

load_dotenv()

logger = get_logger()

# Initialize API key rotator for image generation
image_rotator = APIKeyRotator("image")


def generate_image(prompt: str) -> dict:
    """
    Generate an image from a text prompt with automatic API key fallback.
    
    Returns:
        {"type": "image", "url": "...", "prompt": "..."} on success
        {"type": "error", "message": "..."} on failure
    """
    logger.info(f"🖼️ Generating image for prompt: {prompt}")

    max_retries = len(image_rotator.keys)
    retry_count = 0

    while retry_count < max_retries:
        try:
            current_key = image_rotator.get_current_key()
            image_client = Client(api_key=current_key)

            logger.info(f"🎨 Calling Imagen (key #{image_rotator.current_index + 1}/{image_rotator.get_status()['total_keys']})...")

            result = image_client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config={"number_of_images": 1}
            )

            image = result.generated_images[0]
            logger.info("✅ Image generated successfully")
            
            return {
                "type": "image",
                "url": image.image_uri,
                "prompt": prompt,
            }

        except (ClientError, APIError) as e:
            error_msg = str(e).lower()
            
            # Check for quota/token exhaustion errors
            if any(keyword in error_msg for keyword in ["quota", "exhausted", "rate limit", "429", "403"]):
                logger.warning(f"⚠️ Token quota hit on image key #{image_rotator.current_index + 1}: {e}")
                
                if image_rotator.rotate_to_next_key():
                    retry_count += 1
                    logger.info(f"🔄 Retrying with next image API key... (attempt {retry_count}/{max_retries})")
                    continue
                else:
                    return {
                        "type": "error",
                        "message": "❌ All Image API keys exhausted. Please add more API keys or wait for quota reset."
                    }
            
            # For other errors, fail immediately
            logger.error(f"❌ Image generation error (non-quota): {e}")
            return {
                "type": "error",
                "message": "❌ Image generation failed. Try again."
            }

        except Exception as e:
            logger.error(f"❌ Unexpected error in image generation: {e}")
            return {
                "type": "error",
                "message": "❌ Unexpected error occurred. Try again."
            }

    return {
        "type": "error",
        "message": "❌ Image API key rotation failed. No keys available."
    }
