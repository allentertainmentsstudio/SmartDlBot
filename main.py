import os
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN
from utils import LOGGER

# Import the handlers
from youtube.youtube import setup_downloader_handler
from pinterest.pinterest import setup_pinterest_handler
from facebook.facebook import setup_dl_handlers
from spotify.spotify import setup_spotify_handler
from tiktok.tiktok import setup_tt_handler
from instagram.instagram import setup_in_handlers
from adminpanel.restart.restart import setup_restart_handler
from adminpanel.admin.admin import setup_admin_handler
from adminpanel.logs.logs import setup_logs_handler

# Setup minimal Flask server to prevent Heroku R10 error
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Smart Tool Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# Start Flask in background
Thread(target=run_flask).start()

# Initialize the bot client
app = Client(
    "app_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Setup all handlers
setup_downloader_handler(app)
setup_pinterest_handler(app)
setup_dl_handlers(app)
setup_spotify_handler(app)
setup_restart_handler(app)
setup_admin_handler(app)
setup_logs_handler(app)
setup_in_handlers(app)
setup_tt_handler(app)

# ---------------- START COMMAND -----------------
@app.on_message(filters.command(["start"], prefixes=["/", "."]) & filters.private)
async def send_start_message(client, message):
    chat_id = message.chat.id
    full_name = f"{message.from_user.first_name} {message.from_user.last_name}" if message.from_user.last_name else message.from_user.first_name

    animation_message = await message.reply_text("<b>Starting Smart Tool ⚙️...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)
    await animation_message.edit_text("<b>Generating Session Keys Please Wait...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)
    await animation_message.delete()

    start_message = (
        f"<b>Hi {full_name}! Welcome To This Bot...</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b><a href='tg://user?id=7892805795'>Anuj Kumar ⚙️</a></b>: The ultimate toolkit on Telegram, offering Facebook,YouTube,Pinterest,Spotify Downloader. Simplify your tasks with ease!\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Don't Forget To <a href='https://t.me/log_channel_a'>Join Here</a> For Updates!</b>"
    )

    # ✅ Send start message as photo with caption
    await message.reply_photo(
        photo="https://i.ibb.co/BHjYbjXw/7168219724-29232.jpg",
        caption=start_message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Help", callback_data="help_menu"),
             InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new&admin=post_messages+delete_messages+edit_messages+pin_messages+change_info+invite_users+promote_members")],
            [InlineKeyboardButton("🔄 Updates", url="https://t.me/log_channel_a"),
             InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")]
        ])
    )

# ---------------- CALLBACKS -----------------
@app.on_callback_query(filters.regex("help_menu"))
async def help_menu_callback(client: Client, callback_query: CallbackQuery):
    help_message = (
        "<b>🎥 Social Media and Music Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>USAGE:</b>\n"
        "Download videos and tracks from popular platforms using these commands:\n\n"
        "➢ <b>/fb [Video URL]</b> - Download a Facebook video.\n"
        "➢ <b>/pin [Video URL]</b> - Download a Pinterest video.\n"
        "➢ <b>/tt [Video URL]</b> - Download a TikTok video.\n"
        "➢ <b>/in [Video URL]</b> - Download Instagram Reels.\n"
        "➢ <b>/sp [Track URL]</b> - Download a Spotify track.\n"
        "➢ <b>/yt [Video URL]</b> - Download a YouTube video.\n"
        "➢ <b>/song [Video URL]</b> - Download as MP3\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔔 For Bot Updates: <a href='https://t.me/log_channel_a'>Join Now</a>"
    )

    await callback_query.message.edit_text(
        help_message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="start_menu")]
        ])
    )

@app.on_callback_query(filters.regex("about_me"))
async def about_me_callback(client: Client, callback_query: CallbackQuery):
    about_message = (
        "<b>Name:</b> Smart Tool ⚙️\n"
        "<b>Version:</b> 3.0 (Beta Testing)\n\n"
        "<b>Creator:</b> <a href='https://t.me/anujedits76'>Anuj Kumar👨‍💻</a>\n"
        "<b>Tech:</b> Python · Pyrogram · Telethon · MongoDB\n"
        "<b>About:</b> Download from YouTube, Instagram, Facebook, Pinterest, TikTok, Spotify.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔔 Updates: <a href='https://t.me/log_channel_a'>Join Here</a>"
    )

    await callback_query.message.edit_text(
        about_message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="start_menu")]
        ])
    )

@app.on_callback_query(filters.regex("start_menu"))
async def start_menu_callback(client: Client, callback_query: CallbackQuery):
    full_name = f"{callback_query.from_user.first_name} {callback_query.from_user.last_name}" if callback_query.from_user.last_name else callback_query.from_user.first_name

    start_message = (
        f"<b>Hi {full_name}! Welcome To This Bot...</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b><a href='tg://user?id=7892805795'>Anuj Kumar ⚙️</a></b>: The ultimate toolkit on Telegram, offering Facebook,YouTube,Pinterest,Spotify Downloader. Simplify your tasks with ease!\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Don't Forget To <a href='https://t.me/log_channel_a'>Join Here</a> For Updates!</b>"
    )

    await callback_query.message.edit_text(
        start_message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Help", callback_data="help_menu"),
             InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new&admin=post_messages+delete_messages+edit_messages+pin_messages+change_info+invite_users+promote_members")],
            [InlineKeyboardButton("🔄 Updates", url="https://t.me/log_channel_a"),
             InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")]
        ]),
        disable_web_page_preview=True,
    )

# Final confirmation that the bot has started
print("✅ Bot Successfully Started and Flask is running on Heroku.")
app.run()    # Send video
    caption = f"🎥 **Title**: {reel_info['title']}\n🔗 [Watch on Instagram]({reel_info['webpage_url']})"
    async with aiofiles.open(reel_info["filename"],'rb') as f:
        await client.send_video(chat_id, await f.read(), caption=caption, supports_streaming=True)
    os.remove(reel_info["filename"])
    await downloading_msg.delete()

# ---------------- Start Bot ----------------
print("✅ Bot Successfully Started.")
app.run()
