from google import genai
from google.genai.errors import ClientError
from config import Config
from config import Config
from dotenv import load_dotenv
import os
from logger import get_logger


load_dotenv()
logger = get_logger()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_llm(user_text, history=""):

    prompt = f"""
{Config.SYSTEM_PROMPT}

Conversation history:
{history}

User: {user_text}
Assistant:
"""

    try:
        logger.info("Calling Gemini...")

        response = client.models.generate_content(
            model=Config.MODEL,
            contents=prompt
        )

        return response.text

    except ClientError as e:
        logger.error(f"Gemini quota hit: {e}")
        return "⚠️ Nova is cooling down (API limit hit). Try again in a few seconds."

    except Exception as e:
        logger.error(f"Gemini failed: {e}")
        return "⚠️ Something went wrong. Try again."
