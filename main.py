import os
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN

# Handlers setup (these already register commands)
from youtube.youtube import setup_downloader_handler, download_video as yt_download
from pinterest.pinterest import setup_pinterest_handler, download_video as pin_download
from facebook.facebook import setup_dl_handlers, download_video as fb_download
from spotify.spotify import setup_spotify_handler, download_track as sp_download
from tiktok.tiktok import setup_tt_handler, download_video as tt_download
from instagram.instagram import setup_in_handlers, download_video as in_download

# Admin panel
from adminpanel.restart.restart import setup_restart_handler
from adminpanel.admin.admin import setup_admin_handler
from adminpanel.logs.logs import setup_logs_handler

# Flask server for Replit
flask_app = Flask(__name__)
@flask_app.route('/')
def index():
    return "Smart Tool Bot is running!"
Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()

# Bot client
app = Client("app_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Setup handlers
setup_downloader_handler(app)
setup_pinterest_handler(app)
setup_dl_handlers(app)
setup_spotify_handler(app)
setup_restart_handler(app)
setup_admin_handler(app)
setup_logs_handler(app)
setup_in_handlers(app)
setup_tt_handler(app)

# ---------------- User Quality Storage ----------------
USER_QUALITY = {}  # chat_id -> quality
PENDING_DOWNLOAD = {}  # chat_id -> (platform, url)

QUALITY_MAP = {
    "A": "144p", "B": "240p", "C": "360p", "D": "480p", "E": "720p",
    "F": "1080p", "G": "2K", "H": "4K", "I": "8K", "J": "Audio Only",
    "K": "Low", "L": "Medium", "M": "High", "N": "Very High", "O": "Ultra HD",
    "P": "144p", "Q": "240p", "R": "360p", "S": "480p", "T": "720p",
    "U": "1080p", "V": "2K", "W": "4K", "X": "8K", "Y": "Audio Only", "Z": "Best"
}

# ---------------- Start Command ----------------
@app.on_message(filters.command(["start"], prefixes=["/", "."]) & filters.private)
async def start_command(client, message):
    chat_id = message.chat.id
    full_name = f"{message.from_user.first_name} {message.from_user.last_name}" if message.from_user.last_name else message.from_user.first_name

    animation = await message.reply_text("<b>Starting Smart Tool ⚙️...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)
    await animation.edit_text("<b>Generating Session Keys Please Wait...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)

    start_caption = (
        f"<b>Hi {full_name}! Welcome To This Bot...</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b><a href='tg://user?id=7892805795'>Anuj Kumar ⚙️</a></b>: Download videos and tracks from Facebook, YouTube, Pinterest, Spotify, TikTok, Instagram.\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Don't Forget To <a href='https://t.me/log_channel_a'>Join Here</a> For Updates!</b>"
    )

    await client.send_photo(
        chat_id=chat_id,
        photo="https://i.ibb.co/BHjYbjXw/7168219724-29232.jpg",
        caption=start_caption,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Help", callback_data="help_menu"),
                InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new")
            ],
            [
                InlineKeyboardButton("🔄 Updates", url="https://t.me/log_channel_a"),
                InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")
            ],
            [
                InlineKeyboardButton(ltr, callback_data=f"quality_{ltr}") for ltr in "ABCDEFGHIJKLM"
            ],
            [
                InlineKeyboardButton(ltr, callback_data=f"quality_{ltr}") for ltr in "NOPQRSTUVWXYZ"
            ]
        ]),
        disable_web_page_preview=True
    )

    await animation.delete()

# ---------------- Quality Button Callback ----------------
@app.on_callback_query(filters.regex(r"quality_([A-Z])"))
async def quality_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.from_user.id
    letter = callback_query.data.split("_")[1]
    quality = QUALITY_MAP.get(letter, "720p")
    USER_QUALITY[chat_id] = quality
    await callback_query.answer(f"✅ Selected Quality: {quality}", show_alert=True)

    # Start pending download if exists
    if chat_id in PENDING_DOWNLOAD:
        platform, url = PENDING_DOWNLOAD.pop(chat_id)
        await callback_query.message.reply_text(f"Starting {platform.upper()} download in {quality}...")
        
        if platform == "yt":
            await yt_download(client, chat_id, url, quality)
        elif platform == "tt":
            await tt_download(client, chat_id, url, quality)
        elif platform == "in":
            await in_download(client, chat_id, url, quality)
        elif platform == "fb":
            await fb_download(client, chat_id, url, quality)
        elif platform == "pin":
            await pin_download(client, chat_id, url, quality)
        elif platform == "sp":
            await sp_download(client, chat_id, url, quality)

# ---------------- Command Interceptors for all platforms ----------------
def create_command(platform_name, download_func):
    @app.on_message(filters.command(platform_name) & filters.private)
    async def command(client, message):
        chat_id = message.chat.id
        try:
            url = message.text.split(" ", 1)[1]
        except IndexError:
            await message.reply_text("❌ Please provide a URL.")
            return
        
        if chat_id in USER_QUALITY:
            quality = USER_QUALITY[chat_id]
            await message.reply_text(f"Starting {platform_name.upper()} download in {quality}...")
            await download_func(client, chat_id, url, quality)
        else:
            PENDING_DOWNLOAD[chat_id] = (platform_name, url)
            await message.reply_text("✅ Please select a quality first using the A–Z buttons above.")

# Register all platform commands
create_command("yt", yt_download)
create_command("tt", tt_download)
create_command("in", in_download)
create_command("fb", fb_download)
create_command("pin", pin_download)
create_command("sp", sp_download)

# ---------------- Help / About / Start Menu ----------------
@app.on_callback_query(filters.regex("help_menu"))
async def help_callback(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "<b>🎥 Social Media and Music Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "USAGE:\n"
        "➢ /fb [Video URL]\n"
        "➢ /pin [Video URL]\n"
        "➢ /tt [Video URL]\n"
        "➢ /in [Video URL]\n"
        "➢ /sp [Track URL]\n"
        "➢ /yt [Video URL]\n"
        "➢ /song [Video URL]\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔔 Updates: <a href='https://t.me/log_channel_a'>Join Now</a>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_menu")]])
    )

@app.on_callback_query(filters.regex("about_me"))
async def about_callback(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "<b>Name:</b> Smart Tool ⚙️\n"
        "<b>Version:</b> 3.0 (Beta)\n"
        "<b>Creator:</b> <a href='https://t.me/anujedits76'>Anuj Kumar👨‍💻</a>\n"
        "<b>Tech:</b> Python · Pyrogram · Telethon · MongoDB\n"
        "<b>About:</b> Download from YouTube, Instagram, Facebook, Pinterest, TikTok, Spotify\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔔 Updates: <a href='https://t.me/log_channel_a'>Join Here</a>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_menu")]])
    )

@app.on_callback_query(filters.regex("start_menu"))
async def start_menu_callback(client: Client, query: CallbackQuery):
    full_name = f"{query.from_user.first_name} {query.from_user.last_name}" if query.from_user.last_name else query.from_user.first_name
    await query.message.edit_text(
        f"<b>Hi {full_name}! Welcome To This Bot...</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b><a href='tg://user?id=7892805795'>Anuj Kumar ⚙️</a></b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Don't Forget To <a href='https://t.me/log_channel_a'>Join Here</a> For Updates!</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Help", callback_data="help_menu"),
                InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new")
            ],
            [
                InlineKeyboardButton("🔄 Updates", url="https://t.me/log_channel_a"),
                InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")
            ]
        ]),
        disable_web_page_preview=True
    )

# ---------------- Run Bot ----------------
import time
while True:
    try:
        print("✅ Bot Successfully Started and Flask is running.")
        app.run()
    except Exception as e:
        print(f"⚠️ Bot crashed: {e}\nRestarting in 5 seconds...")
        time.sleep(5)
