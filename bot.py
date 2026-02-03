from telegram.ext import ApplicationBuilder, MessageHandler, filters
from config import Config
from logger import get_logger

from llm import ask_llm
from memory import save_message, get_history
from cache import cache_history, get_cache
import asyncio

logger = get_logger()


async def reply(update, context):
    user_id = str(update.message.chat_id)
    text = update.message.text

    logger.info(f"Message from {user_id}")

    await update.message.reply_text("Thinking...")

    await asyncio.sleep(1)

    history = get_cache(user_id) or get_history(user_id)

    answer = ask_llm(text, history)

    save_message(user_id, "user", text)
    save_message(user_id, "assistant", answer)

    cache_history(user_id, f"user: {text}")
    cache_history(user_id, f"assistant: {answer}")
    logger.info(f"Sending reply to {user_id}")
    try:
        await update.message.reply_text(answer)
        logger.info(f"Reply successfully sent to {user_id}")

    except Exception as e:
        logger.error(f"Reply failed: {e}")


logger.info("Nova started 🚀")

app = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, reply))

app.run_polling()
