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

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Pinterest", callback_data="pinterest")],
        [InlineKeyboardButton("TikTok", callback_data="tiktok")],
    ]

    await update.message.reply_text(
        "*PinoDownloader Bot*\n\nChoose a platform below and send your video link.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["platform"] = query.data
    await query.edit_message_text(
        f"Selected: {query.data.upper()}\n\nNow send me your video link."
    )
	


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    platform = context.user_data.get("platform")

    if not platform:
        await update.message.reply_text("Please choose a platform first using /start")
        return

    if platform == "pinterest":
        if not ("pinterest.com" in text or "pin.it" in text):
            await update.message.reply_text(
                "Invalid Pinterest link.\n\n"
                "Please send a valid Pinterest video link like:\n"
                "• https://pin.it/xxxxx\n"
                "• https://pinterest.com/pin/xxxxx\n"
                "• https://www.pinterest.com/pin/xxxxx"
            )
            return
            
    elif platform == "tiktok":
        if not ("tiktok.com" in text or "vm.tiktok.com" in text):
            await update.message.reply_text(
                "Invalid TikTok link.\n\n"
                "Please send a valid TikTok video link like:\n"
                "• https://vm.tiktok.com/xxxxx\n"
                "• https://tiktok.com/@user/video/xxxxx\n"
                "• https://www.tiktok.com/@user/video/xxxxx"
            )
            return

    await update.message.reply_text("Processing your video...")

    try:
        video_url = None

        if platform == "pinterest":
            video_url = extract_pinterest_video(text)

        elif platform == "tiktok":
            video_url = extract_tiktok_video(text)

        if not video_url:
            await update.message.reply_text(
                "Could not extract video from this link.\n\n"
                f"Please make sure you sent a valid {platform.upper()} video link.\n"
                "The link should point to a video post, not a profile or homepage."
            )
            return

        await update.message.reply_text("Downloading video...")

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        video_data = requests.get(video_url, headers=headers, timeout=60).content

        await update.message.reply_video(
            video=video_data,
            supports_streaming=True
        )

    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "Request timed out. The link might be invalid or the server is slow.\n\n"
            f"Please send a valid {platform.upper()} video link."
        )
    except requests.exceptions.RequestException:
        await update.message.reply_text(
            "Failed to download the video.\n\n"
            f"Please check your {platform.upper()} link and try again."
        )
    except Exception as e:
        await update.message.reply_text(
            f"Error: {str(e)}\n\n"
            f"This doesn't look like a valid {platform.upper()} video link.\n"
            "Please send a correct video link from the selected platform."
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()