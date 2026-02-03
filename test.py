import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
modal_name = os.getenv("model_name")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name=modal_name)  # fast + cheap

def ask_gemini(text):
    response = model.generate_content(text)
    return response.text


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    await update.message.reply_text("Thinking...")

    answer = ask_gemini(user_text)

    await update.message.reply_text(answer)


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, reply))

print("Bot running...")
app.run_polling()
