# main.py - Replit Optimized Smart Tool Bot
import os, asyncio, re, shutil, subprocess
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from yt_dlp import YoutubeDL

from config import API_ID, API_HASH, BOT_TOKEN

# ------------------------
# Flask Server for 24/7
# ------------------------
flask_app = Flask(__name__)
@flask_app.route('/')
def index(): return "Smart Tool Bot is running!"
Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))).start()

# ------------------------
# Initialize Pyrogram Bot
# ------------------------
app = Client("app_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ------------------------
# Queue System for Multiple Users
# ------------------------
download_queue = asyncio.Queue()

async def worker():
    while True:
        callback_query, url, quality = await download_queue.get()
        try:
            await process_download(callback_query, url, quality)
        except Exception as e:
            await callback_query.message.reply(f"❌ Error: {e}")
        download_queue.task_done()

# Start 3 workers for Replit safe parallel downloads
for _ in range(3):
    asyncio.create_task(worker())

# ------------------------
# Platforms Regex
# ------------------------
PLATFORM_REGEX = {
    "yt": r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+",
    "tt": r"(https?://)?(www\.)?(tiktok\.com)/.+",
    "in": r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/.+",
    "fb": r"(https?://)?(www\.)?(facebook\.com)/.+",
    "pin": r"(https?://)?(www\.)?(pinterest\.com)/.+",
    "sp": r"(https?://)?(open\.spotify\.com)/.+"
}

# ------------------------
# Quality Buttons
# ------------------------
def quality_buttons(platform, url):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("144p", callback_data=f"{platform}_144|{url}"),
         InlineKeyboardButton("360p", callback_data=f"{platform}_360|{url}"),
         InlineKeyboardButton("720p", callback_data=f"{platform}_720|{url}")],
        [InlineKeyboardButton("1080p", callback_data=f"{platform}_1080|{url}"),
         InlineKeyboardButton("2K", callback_data=f"{platform}_2k|{url}"),
         InlineKeyboardButton("MP3", callback_data=f"{platform}_mp3|{url}")]
    ])

# ------------------------
# /start Handler
# ------------------------
@app.on_message(filters.command(["start"], prefixes=["/", "."]) & filters.private)
async def send_start_message(client, message):
    full_name = f"{message.from_user.first_name} {message.from_user.last_name}" if message.from_user.last_name else message.from_user.first_name
    start_caption = (
        "<b>👋🏻 Hello!</b> <i>I can help you download videos and images from:</i>\n\n"
        "🌐 <b>YouTube</b> 🌐 <b>Instagram</b> 🌐 <b>TikTok</b>\n"
        "🌐 <b>Pinterest</b> 🌐 <b>Snapchat</b> 🌐 <b>Likee</b>\n"
        "🌍 <b>VK</b> 🌐 <b>Facebook</b> 🌐 <b>Threads</b>\n"
        "🎵 <b>Music</b>\n\n"
        "<i>• Send me a link or song name to download instantly.\n• Works in groups too!</i>"
    )
    await message.reply_photo(
        photo="https://i.ibb.co/BHjYbjXw/7168219724-29232.jpg",
        caption=start_caption,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Help", callback_data="help_menu"),
             InlineKeyboardButton("➕ Add Me", url="https://t.me/Media_downloader_ak_bot?startgroup=new")],
            [InlineKeyboardButton("🔄 Updates", url="https://t.me/log_channel_a")]
        ])
    )

# ------------------------
# Auto link handler
# ------------------------
@app.on_message(filters.private & ~filters.command)
async def auto_handler(client, message):
    text = message.text.strip()
    for platform, regex in PLATFORM_REGEX.items():
        if re.match(regex, text):
            await message.reply("🎛️ Link detected! Select quality:", reply_markup=quality_buttons(platform, text))
            return
    # Song search
    msg = await message.reply("🔍 Searching song...")
    loop = asyncio.get_event_loop()
    def run_song():
        ydl_opts = {
            'format':'bestaudio/best',
            'quiet':True,
            'noplaylist':True,
            'outtmpl':'downloads/%(title)s.%(ext)s',
            'postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}]
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{text}", download=True)
            video = info['entries'][0]
            filename = os.path.splitext(ydl.prepare_filename(video))[0]+".mp3"
            return video['title'], filename
    try:
        title, file_path = await loop.run_in_executor(None, run_song)
        await msg.edit("🎵 Downloading...")
        await message.reply_audio(file_path, caption=f"🎵 {title}")
        os.remove(file_path)
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

# ------------------------
# Callback for Quality Selection
# ------------------------
@app.on_callback_query(filters.regex(r"(yt|tt|in|fb|pin)_(144|360|720|1080|2k|mp3)\|"))
async def universal_quality(client, callback_query: CallbackQuery):
    data = callback_query.data.split("|")
    platform, quality = data[0].split("_")
    url = data[1]
    await callback_query.message.edit(f"⬇️ Added to queue for download...")
    await download_queue.put((callback_query, url, quality))

# ------------------------
# Process Download
# ------------------------
async def process_download(callback_query, url, quality):
    msg = await callback_query.message.edit("⬇️ Processing download...")
    loop = asyncio.get_event_loop()
    def run():
        ydl_opts = {
            'format': f'bestvideo[height<={quality.replace("k","000")}]+bestaudio/best' if quality!="mp3" else 'bestaudio/best',
            'noplaylist':False,
            'quiet':True,
            'outtmpl':'downloads/%(title)s.%(ext)s',
            'postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}] if quality=="mp3" else []
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            files = []
            videos = info.get('entries', [info])
            for video in videos:
                filename = os.path.splitext(ydl.prepare_filename(video))[0]+(".mp3" if quality=="mp3" else ".mp4")
                # ✅ Limit size for Replit (~1.5GB)
                if os.path.exists(filename) and os.path.getsize(filename) > 1.5*1024*1024*1024:
                    files.append((video['title'], None))  # skip too large
                else:
                    files.append((video['title'], filename))
            return files
    files = await loop.run_in_executor(None, run)
    for title, file_path in files:
        if file_path is None:
            await callback_query.message.reply(f"⚠️ Skipped {title} (Too Large for Replit)")
            continue
        try:
            if quality=="mp3":
                await callback_query.message.reply_audio(file_path, caption=f"🎵 {title}")
            else:
                await callback_query.message.reply_video(file_path, caption=f"📥 {title}")
            os.remove(file_path)
        except:
            await callback_query.message.reply(f"❌ Failed: {title}")
    await msg.edit("✅ Done!")

# ------------------------
# Cleanup downloads folder every start
# ------------------------
shutil.rmtree("downloads", ignore_errors=True)
os.makedirs("downloads", exist_ok=True)

# ------------------------
# Run Bot
# ------------------------
print("✅ Replit Optimized Smart Tool Bot running.")
app.run()
