from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram import Update
import os
from adk_runner import run_adk_agent
from memory.cache import get_cache, clear_cache
from config.logger import get_logger
import json
import html

def safe_html(text: str) -> str:
    return html.escape(text)

logger = get_logger()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I'm your assistant — say hi or ask for today's emails.\n\n"
        "Commands:\n"
        "/clear - Clear conversation history"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    text = update.message.text

    logger.info(f"📩 Received message from {user_id}: {text}")

    await update.message.reply_text("🤖 Thinking...")

    response = await run_adk_agent(
        user_id=user_id,
        query_text=text
    )

    # If response is a string, just send it as text
    if isinstance(response, str):
        await update.message.reply_text(response)
        return

    # If response is a dict with image data
    if isinstance(response, dict) and response.get("type") == "image":
        await update.message.reply_photo(
            photo=response["url"],
            caption=(
                "<b>Nova 🤖</b>\n\n"
                f"🖼️ <i>Generated image for:</i>\n"
                f"<code>{safe_html(response['prompt'])}</code>"
            ),
            parse_mode="HTML"
        )
        return

    # Fallback if response is dict but not image type
    if isinstance(response, dict):
        await update.message.reply_text(json.dumps(response, indent=2))
        return


async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear the user's conversation history from Redis."""
    user_id = str(update.message.chat_id)
    if clear_cache(user_id):
        await update.message.reply_text("✅ Conversation history cleared!")
    else:
        await update.message.reply_text("❌ Failed to clear history")


if __name__ == "__main__":
    logger.info("Nova started")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()