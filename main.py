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


from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram import Update

from adk_runner import run_sync  # Import the function we built earlier

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I’m your assistant — say hi or ask for today's emails."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "hi" in text or "hello" in text or "hey" in text:
        # Simple conversational greeting
        await update.message.reply_text("Hey there! How can I help you today?")
        return

    # Trigger for email summary
    if "mail" in text or "email" in text:
        await update.message.reply_text("⏳ Let me check your emails...")

        # Run your ADK agent
        response = run_sync(
            user_id=str(update.message.chat_id),
            query_text="fetch and summarize today’s emails"
        )

        await update.message.reply_text(response)
        return

    # Fallback - echo or generic reply
    await update.message.reply_text("Sorry, I didn’t get that — try asking for today’s mail!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()