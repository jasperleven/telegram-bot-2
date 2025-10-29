#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
import subprocess
import asyncio

# --- Установка зависимостей ---
required_packages = ["python-telegram-bot>=20.0", "yt-dlp", "nest_asyncio"]
for package in required_packages:
    try:
        __import__(package.split('>=')[0].replace('-', '_'))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# --- Импорты ---
import nest_asyncio
nest_asyncio.apply()  # Для Jupyter / Anaconda

from yt_dlp import YoutubeDL
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- Ваш токен ---
BOT_TOKEN = "BOT_TOKEN"

# --- Сброс webhook для устранения конфликта ---
bot = Bot(BOT_TOKEN)
bot.delete_webhook()
print("Webhook сброшен, можно использовать polling.")

# --- Настройки yt_dlp ---
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
    'no_warnings': True,
}

os.makedirs('downloads', exist_ok=True)

# --- Команды бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне ссылку на YouTube-видео, и я скачаю его аудио в mp3."
    )

# --- Скачивание аудио ---
async def download_audio(url: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download_audio_sync, url)

def _download_audio_sync(url: str):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        filename = os.path.splitext(filename)[0] + ".mp3"
        return filename, info.get('title', 'audio')

# --- Обработка сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("⏳ Загружаю аудио, это может занять несколько секунд...")
    try:
        file_path, title = await download_audio(url)
        if os.path.exists(file_path):
            # Открываем файл через with, чтобы дескриптор закрылся после отправки
            with open(file_path, 'rb') as audio_file:
                await update.message.reply_audio(audio=audio_file, title=title)
            await update.message.reply_text("✅ Аудио успешно загружено!")
            os.remove(file_path)
        else:
            await update.message.reply_text("❌ Ошибка: файл не найден после скачивания.")
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка при скачивании: {e}")

# --- Запуск бота ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    await app.run_polling(close_loop=False)

# --- Запуск для Jupyter / Anaconda и обычного .py ---
asyncio.get_event_loop().create_task(main())


# In[ ]:




