# main.py
import os
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN
from utils import LOGGER

# Import downloader handlers
from youtube.youtube import setup_downloader_handler
from pinterest.pinterest import setup_pinterest_handler
from facebook.facebook import setup_dl_handlers
from spotify.spotify import setup_spotify_handler
from tiktok.tiktok import setup_tt_handler
from instagram.instagram import setup_in_handlers
from adminpanel.restart.restart import setup_restart_handler
from adminpanel.admin.admin import setup_admin_handler
from adminpanel.logs.logs import setup_logs_handler

# =========================
# Flask server to keep Replit/Heroku alive
# =========================
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Smart Tool Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

Thread(target=run_flask).start()

# =========================
# Initialize Bot
# =========================
app = Client(
    "app_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# Setup Handlers
# =========================
setup_downloader_handler(app)
setup_pinterest_handler(app)
setup_dl_handlers(app)
setup_spotify_handler(app)
setup_restart_handler(app)
setup_admin_handler(app)
setup_logs_handler(app)
setup_in_handlers(app)
setup_tt_handler(app)

# =========================
# /start message
# =========================
START_PHOTO = "https://i.ibb.co/BHjYbjXw/7168219724-29232.jpg"
START_TEXT = (
    "**👋🏻 Hello📥 I can help you download videos and images from:**\n"
    "🌐 **YouTube** 🌐 **Instagram** 🌐 **TikTok** 🌐 **Pinterest** 🌐 **Snapchat** 🌐 **Likee** 🌍 **VK** 🌐 **Facebook** 🌐 **Threads** 🎵 **Music**\n"
    "*• To download a video or song, send me the link or just type the song/video name (works in groups too).*"
)

@app.on_message(filters.private & filters.text & filters.command("start"))
async def start_msg(client, message):
    await message.reply_photo(
        photo=START_PHOTO,
        caption=START_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Help", callback_data="help_menu"),
             InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new&admin=post_messages+delete_messages+edit_messages+pin_messages+change_info+invite_users+promote_members")],
            [InlineKeyboardButton("🔄 Updates", url="https://t.me/log_channel_a"),
             InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")]
        ])
    )

@app.on_callback_query(filters.regex("help_menu"))
async def help_menu(client, cq: CallbackQuery):
    help_text = (
        "**🎥 Social Media and Music Downloader**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "**USAGE:**\n"
        "Just send the link of the video or the song name, bot will automatically download it.\n"
        "Supported Platforms:\n"
        "➢ YouTube, TikTok, Instagram, Facebook, Pinterest, Spotify, VK, Likee\n"
        "**VIDEO QUALITY:**\n"
        "You can select quality from Low → 4K if available.\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔔 For Updates: [Join Now](https://t.me/log_channel_a)"
    )
    await cq.message.edit_text(help_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_menu")]]))

@app.on_callback_query(filters.regex("about_me"))
async def about_me(client, cq: CallbackQuery):
    about_text = (
        "**Smart Tool ⚙️**\n"
        "Version: 3.0 (Beta)\n"
        "Creator: [Anuj Kumar👨‍💻](https://t.me/anujedits76)\n"
        "Tech: Python · Pyrogram · Telethon · MongoDB\n"
        "Downloads from: YouTube, Instagram, Facebook, Pinterest, TikTok, Spotify\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Updates: [Join Here](https://t.me/log_channel_a)"
    )
    await cq.message.edit_text(about_text, parse_mode=ParseMode.MARKDOWN,
                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_menu")]]))

@app.on_callback_query(filters.regex("start_menu"))
async def start_menu(client, cq: CallbackQuery):
    await start_msg(client, cq.message)

# =========================
# Ready to deploy
# =========================
print("✅ Bot Successfully Started and Flask is running on port 5000.")
app.run()
