import os
import asyncio
from threading import Thread
from pathlib import Path
import aiofiles
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN, COMMAND_PREFIX
from youtube.youtube import setup_downloader_handler
from pinterest.pinterest import setup_pinterest_handler
from facebook.facebook import setup_dl_handlers
from spotify.spotify import setup_spotify_handler
from tiktok.tiktok import setup_tt_handler
from instagram.instagram import InstagramDownloader
from adminpanel.restart.restart import setup_restart_handler
from adminpanel.admin.admin import setup_admin_handler
from adminpanel.logs.logs import setup_logs_handler
import yt_dlp

# ---------------- Flask Server ----------------
flask_app = Flask(__name__)
@flask_app.route('/')
def index():
    return "Smart Tool Bot is running!"

Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()

# ---------------- Bot Client ----------------
app = Client("app_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------------- Setup handlers ----------------
setup_downloader_handler(app)
setup_pinterest_handler(app)
setup_dl_handlers(app)
setup_spotify_handler(app)
setup_restart_handler(app)
setup_admin_handler(app)
setup_logs_handler(app)
setup_tt_handler(app)

# ---------------- Quality Setup ----------------
USER_QUALITY = {}  # chat_id -> quality

QUALITY_MAP = {
    "A":"144p","B":"240p","C":"360p","D":"480p","E":"720p","F":"1080p",
    "G":"2K","H":"4K","I":"8K","J":"Audio Only","K":"Low","L":"Medium",
    "M":"High","N":"Very High","O":"Ultra HD","P":"144p","Q":"240p",
    "R":"360p","S":"480p","T":"720p","U":"1080p","V":"2K","W":"4K",
    "X":"8K","Y":"Audio Only","Z":"Best","BEST":"best"
}

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
ig_downloader = InstagramDownloader(TEMP_DIR)

# ---------------- Progress Bar ----------------
async def progress_bar(current, total, status_msg, start_time, last_update_time):
    elapsed = time.time() - start_time
    percentage = (current/total)*100
    progress = "▓"*int(percentage//5) + "░"*(20-int(percentage//5))
    speed = current/elapsed/1024/1024
    uploaded = current/1024/1024
    total_size = total/1024/1024
    if time.time() - last_update_time[0] < 1:
        return
    last_update_time[0] = time.time()
    try:
        await status_msg.edit(
            f"📥 Upload Progress 📥\n\n{progress}\n\n"
            f"🚧 Percentage: {percentage:.2f}%\n"
            f"⚡️ Speed: {speed:.2f} MB/s\n"
            f"📶 Uploaded: {uploaded:.2f} MB / {total_size:.2f} MB"
        )
    except:
        pass

# ---------------- Start Command ----------------
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    chat_id = message.chat.id
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()

    animation = await message.reply_text("<b>Starting Smart Tool ⚙️...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.5)
    await animation.edit_text("<b>Generating Session Keys Please Wait...</b>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.5)
    await animation.delete()

    caption = (
        f"<b>Hi {full_name}! Welcome To This Bot...</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b><a href='tg://user?id=7892805795'>Anuj Kumar ⚙️</a></b>: Ultimate toolkit for social media downloads.\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "<b>Don't Forget To <a href='https://t.me/log_channel_a'>Join Here</a> For Updates!</b>"
    )

    await client.send_photo(
        chat_id,
        photo="https://i.ibb.co/BHjYbjXw/7168219724-29232.jpg",
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Help", callback_data="help_menu"),
             InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new")],
            [InlineKeyboardButton("🔄 Updates", url="https://t.me/log_channel_a"),
             InlineKeyboardButton("ℹ️ About Me", callback_data="about_me")],
            [InlineKeyboardButton(ltr, callback_data=f"quality_{ltr}") for ltr in "ABCDEFGHIJKLM"],
            [InlineKeyboardButton(ltr, callback_data=f"quality_{ltr}") for ltr in "NOPQRSTUVWXYZ"]
        ]),
        disable_web_page_preview=True
    )

# ---------------- Quality Callback ----------------
@app.on_callback_query(filters.regex(r"quality_([A-Z])"))
async def quality_callback(client, query: CallbackQuery):
    letter = query.data.split("_")[1]
    USER_QUALITY[query.from_user.id] = QUALITY_MAP.get(letter, "best")
    await query.answer(f"✅ Selected Quality: {USER_QUALITY[query.from_user.id]}", show_alert=True)

# ---------------- Help & About ----------------
@app.on_callback_query(filters.regex("help_menu"))
async def help_cb(client, query: CallbackQuery):
    await query.message.edit_text(
        "<b>🎥 Social Media Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "➢ /fb [URL]\n➢ /pin [URL]\n➢ /tt [URL]\n➢ /in [URL]\n➢ /sp [URL]\n➢ /yt [URL]\n➢ /song [URL]",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_menu")]]),
        disable_web_page_preview=True
    )

@app.on_callback_query(filters.regex("about_me"))
async def about_cb(client, query: CallbackQuery):
    await query.message.edit_text(
        "<b>Smart Tool ⚙️</b>\n<b>Version:</b> 3.0\n<b>Creator:</b> Anuj Kumar\n"
        "Download from all major social media.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_menu")]]),
        disable_web_page_preview=True
    )

@app.on_callback_query(filters.regex("start_menu"))
async def start_menu_cb(client, query: CallbackQuery):
    await start(client, query.message)

# ---------------- Instagram Download Handler ----------------
@app.on_message(filters.command("in") & filters.private)
async def ig_download(client, message):
    chat_id = message.chat.id
    try:
        url = message.text.split(" ",1)[1]
    except IndexError:
        await message.reply_text("❌ Please provide an Instagram link!")
        return

    quality = USER_QUALITY.get(chat_id, "best")
    downloading_msg = await message.reply_text("🔎 Searching Instagram video...")

    # Try main API
    reel_info = None
    try:
        reel_info = await ig_downloader.download_reel(url, downloading_msg)
    except Exception:
        pass

    # Fallback yt-dlp
    if not reel_info or not os.path.exists(reel_info.get("filename","")):
        await downloading_msg.edit_text("⚡ API failed, using yt-dlp fallback...")
        ydl_opts = {
            "format": "bestvideo+bestaudio/best" if quality=="best" else quality,
            "outtmpl": str(TEMP_DIR / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True
        }
        loop = asyncio.get_event_loop()
        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get("title","Instagram Video")
                return {"filename": filename,"title": title,"webpage_url": url}
        try:
            reel_info = await loop.run_in_executor(None,_download)
        except Exception as e:
            await downloading_msg.edit_text(f"❌ Download failed: {e}")
            return

    # Send video
    caption = f"🎥 **Title**: {reel_info['title']}\n🔗 [Watch on Instagram]({reel_info['webpage_url']})"
    async with aiofiles.open(reel_info["filename"],'rb') as f:
        await client.send_video(chat_id, await f.read(), caption=caption, supports_streaming=True)
    os.remove(reel_info["filename"])
    await downloading_msg.delete()

# ---------------- Start Bot ----------------
print("✅ Bot Successfully Started.")
app.run()
