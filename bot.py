from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import os
import requests
from dotenv import load_dotenv

from services.pinterest import extract_pinterest_video
from services.tiktok import extract_tiktok_video
from services.instagram import extract_instagram_video

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(" Pinterest", callback_data="pinterest")],
        [InlineKeyboardButton(" TikTok", callback_data="tiktok")],
        [InlineKeyboardButton(" Instagram", callback_data="instagram")],
    ]

    await update.message.reply_text(
        " *PinoDownloader Bot*\n\n"
        "Choose a platform below and send your video link.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["platform"] = query.data

    await query.edit_message_text(
        f"Selected: {query.data.upper()}\n\n"
        "Now send me your video link."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    platform = context.user_data.get("platform")

    if not platform:
        await update.message.reply_text("Please choose a platform first using /start")
        return

    await update.message.reply_text("Processing your video...")

    try:
        video_url = None

        if platform == "pinterest":
            video_url = extract_pinterest_video(text)

        elif platform == "tiktok":
            video_url = extract_tiktok_video(text)

        elif platform == "instagram":
            video_url = extract_instagram_video(text)

        if not video_url:
            await update.message.reply_text(" Could not extract video.")
            return

        await update.message.reply_text("Downloading video...")

        video_data = requests.get(video_url, timeout=30).content

        await update.message.reply_video(video=video_data)

    except Exception as e:
        await update.message.reply_text(f" Error: {str(e)}")



app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print(" Bot is running...")
app.run_polling()