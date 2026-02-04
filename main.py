# from telegram.ext import ApplicationBuilder, MessageHandler, filters
# from config.config import Config
# from config.logger import get_logger

# from llm.llm import ask_llm
# from memory.memory import save_message, get_history
# from memory.cache import cache_history, get_cache
# import asyncio

# logger = get_logger()

# async def reply(update, context):
#     user_id = str(update.message.chat_id)
#     text = update.message.text

#     logger.info(f"Message from {user_id}")

#     await update.message.reply_text("Thinking...")

#     await asyncio.sleep(1)

#     history = get_cache(user_id) or get_history(user_id)

#     answer = ask_llm(text, history)

#     save_message(user_id, "user", text)
#     save_message(user_id, "assistant", answer)

#     cache_history(user_id, f"user: {text}")
#     cache_history(user_id, f"assistant: {answer}")
#     logger.info(f"Sending reply to {user_id}")
#     try:
#         await update.message.reply_text(answer)
#         logger.info(f"Reply successfully sent to {user_id}")

#     except Exception as e:
#         logger.error(f"Reply failed: {e}")

# logger.info("Nova started")

# app = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
# app.add_handler(MessageHandler(filters.TEXT, reply))

# app.run_polling()


from google import genai
from google.genai.errors import ClientError
from dotenv import load_dotenv
import os

from config.config import Config
from config.logger import get_logger

from agents.web_agent import create_web_agent
from tasks.web_task import create_web_task

from crewai import Crew

import warnings
warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API"
)

warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()
logger = get_logger()


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(user_text: str, history: str = "") -> str:
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
        return "Nova is cooling down (API limit hit). Try again in a few seconds."

    except Exception as e:
        logger.error(f"Gemini failed: {e}")
        return "Something went wrong. Try again."

# -----------------------------------
# CrewAI Execution
# -----------------------------------
def ask_crewai(user_text: str, history: str = "") -> str:
    try:
        logger.info("Calling CrewAI agent...")

        agent = create_web_agent()
        task = create_web_task(agent, user_text, history)

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )

        result = crew.kickoff()
        return str(result)

    except Exception as e:
        logger.error(f"CrewAI failed: {e}")
        logger.info("Falling back to Gemini")
        return ask_gemini(user_text, history)

# -----------------------------------
# Router (Single Responsibility)
# -----------------------------------
def needs_web_search(text: str) -> bool:
    keywords = [
        "latest", "today", "news", "current",
        "price", "update", "release",
        "who is", "what is", "search", "find"
    ]
    return any(k in text.lower() for k in keywords)

# -----------------------------------
# Public API (Telegram calls this)
# -----------------------------------
def ask_llm(user_text: str, history: str = "") -> str:
    if needs_web_search(user_text):
        return ask_crewai(user_text, history)

    return ask_gemini(user_text, history)


if __name__ == "__main__":
    print("Starting test...")
    response = ask_llm("latest news about OpenAI", "")
    print(response)