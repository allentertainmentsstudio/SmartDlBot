import os
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN

# Download handlers
from youtube.youtube import setup_downloader_handler, youtube_download
from pinterest.pinterest import setup_pinterest_handler, pinterest_download
from facebook.facebook import setup_dl_handlers, facebook_download
from spotify.spotify import setup_spotify_handler, spotify_download
from tiktok.tiktok import setup_tt_handler, tiktok_download
from instagram.instagram import setup_in_handlers, instagram_download

# Admin panel handlers
from adminpanel.restart.restart import setup_restart_handler
from adminpanel.admin.admin import setup_admin_handler
from adminpanel.logs.logs import setup_logs_handler

# ---------------- Flask Server ----------------
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Smart Tool Bot is running!"

Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()

# ---------------- Bot Client ----------------
app = Client("app_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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

# ---------------- User Quality Storage ----------------
USER_QUALITY = {}  # key: chat_id, value: quality string

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
    await animation.delete()

    start_caption = (
        f"<b>Hi {full_name}! Welcome To This Bot...</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b><a href='tg://user?id=7892805795'>Anuj Kumar ⚙️</a></b>: The ultimate toolkit on Telegram, offering Facebook, YouTube, Pinterest, Spotify Downloader.\n"
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
                InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new&admin=post_messages+delete_messages+edit_messages+pin_messages+change_info+invite_users+promote_members")
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

# ---------------- Callback Handlers ----------------
@app.on_callback_query(filters.regex("help_menu"))
async def help_callback(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "<b>🎥 Social Media and Music Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>USAGE:</b>\n"
        "➢ /fb [Video URL] - Facebook video\n"
        "➢ /pin [Video URL] - Pinterest video\n"
        "➢ /tt [Video URL] - TikTok video\n"
        "➢ /in [Video URL] - Instagram Reels\n"
        "➢ /sp [Track URL] - Spotify track\n"
        "➢ /yt [Video URL] - YouTube video\n"
        "➢ /song [Video URL] - MP3\n"
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
        "<b><a href='tg://user?id=7892805795'>Anuj Kumar ⚙️</a></b>: The ultimate toolkit on Telegram.\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Don't Forget To <a href='https://t.me/log_channel_a'>Join Here</a> For Updates!</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Help", callback_data="help_menu"),
                InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new&admin=post_messages+delete_messages+edit_messages+pin_messages+change_info+invite_users+promote_members")
            ],
            [
                InlineKeyboardButton("🔄 Updates", url="https://t.me/log_channel_a"),
                InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")
            ]
        ]),
        disable_web_page_preview=True
    )

# ---------------- A-Z Quality Callback ----------------
@app.on_callback_query(filters.regex(r"quality_([A-Z])"))
async def quality_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.from_user.id
    letter = callback_query.data.split("_")[1]
    quality = QUALITY_MAP.get(letter, "Default Quality")
    USER_QUALITY[chat_id] = quality
    await callback_query.answer(f"✅ Selected Quality: {quality}", show_alert=True)

# ---------------- Example: Using Selected Quality in Handlers ----------------
# You need to modify each handler to use USER_QUALITY[chat_id]

# Example for YouTube
@app.on_message(filters.command("yt") & filters.private)
async def download_youtube(client, message):
    chat_id = message.chat.id
    url = message.text.split(" ", 1)[1]
    quality = USER_QUALITY.get(chat_id, "720p")
    video_path = await youtube_download(url, quality)
    await client.send_video(chat_id, video_path)

# Repeat the same in Instagram, TikTok, Facebook, Pinterest, Spotify handlers

print("✅ Bot Successfully Started and Flask is running.")
app.run()
