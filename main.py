from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram import Update
import os
from adk_runner import run_adk_agent  # Import the function we built earlier
from config.logger import get_logger
import json
import html
def safe_html(text: str) -> str:
    return html.escape(text)

logger = get_logger()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I’m your assistant — say hi or ask for today's emails."
    )

# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.message.chat_id)
#     text = update.message.text

#     logger.info(f"Received message from {user_id}: {text}")

#     # Optional typing indicator
#     await update.message.reply_text("Thinking...")

#     logger.info("Forwarding message to ADK agent")

#     response = await run_adk_agent(
#         user_id=user_id,
#         query_text=text
#     )

#     logger.info("ADK agent responded")

#     # Optional: persist for debugging
#     with open("response.json", "w", encoding="utf-8") as f:
#         json.dump({"response": response}, f, indent=2)

#     # Send formatted response
#     await update.message.reply_text(
#         f"<b>Nova</b>\n\n{response}",
#         parse_mode="HTML"
#     )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    text = update.message.text

    logger.info(f"📩 Received message from {user_id}: {text}")

    await update.message.reply_text("🤖 Thinking...")

    response = await run_adk_agent(
        user_id=user_id,
        query_text=text
    )

    await update.message.reply_photo(
    photo=response["url"],
    caption=f"Nova \n\nGenerated image for:\n{response['prompt']}"
    )

    # if isinstance(response, dict) and response.get("type") == "image":
        # await update.message.reply_photo(
        #     photo=response["url"],
        #     caption=(
        #         "<b>Nova 🤖</b>\n\n"
        #         f"🖼️ <i>Generated image for:</i>\n"
        #         f"<code>{response['prompt']}</code>"
        #     ),
        #     parse_mode="HTML"
        # )
        # return

    await update.message.reply_text(response)


if __name__ == "__main__":
    logger.info("Nova started")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()