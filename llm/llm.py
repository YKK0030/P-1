from google import genai
from google.genai.errors import ClientError, APIError
from config.config import Config, APIKeyRotator
from config.logger import get_logger
from dotenv import load_dotenv
import os

load_dotenv()
logger = get_logger()

# Initialize API key rotator
gemini_rotator = APIKeyRotator("gemini")

def get_gemini_client():
    """Get Gemini client with current API key."""
    current_key = gemini_rotator.get_current_key()
    return genai.Client(api_key=current_key)


def ask_llm(user_text: str, history: str = "") -> str:
    """
    Call Gemini with automatic API key fallback on token exhaustion.
    """
    prompt = f"""
{Config.SYSTEM_PROMPT}

Conversation history:
{history}

User: {user_text}
Assistant:
"""

    max_retries = len(gemini_rotator.keys)
    retry_count = 0

    while retry_count < max_retries:
        try:
            client = get_gemini_client()
            logger.info(f"🤖 Calling Gemini (key #{gemini_rotator.current_index + 1}/{gemini_rotator.get_status()['total_keys']})...")

            response = client.models.generate_content(
                model=Config.MODEL,
                contents=prompt
            )

            return response.text

        except (ClientError, APIError) as e:
            error_msg = str(e).lower()
            
            # Check for quota/token exhaustion errors
            if any(keyword in error_msg for keyword in ["quota", "exhausted", "rate limit", "429", "403"]):
                logger.warning(f"⚠️ Token quota hit on key #{gemini_rotator.current_index + 1}: {e}")
                
                if gemini_rotator.rotate_to_next_key():
                    retry_count += 1
                    logger.info(f"🔄 Retrying with next API key... (attempt {retry_count}/{max_retries})")
                    continue
                else:
                    return "❌ All Gemini API keys exhausted. Please add more API keys or wait for quota reset."
            
            # For other errors, fail immediately
            logger.error(f"❌ Gemini error (non-quota): {e}")
            return "❌ Something went wrong with Gemini. Try again."

        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return "❌ Unexpected error occurred. Try again."

    return "❌ API key rotation failed. No keys available."
