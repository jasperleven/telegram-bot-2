#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# Получаем токен из переменной окружения
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в переменных окружения!")

# Путь к cookies (можно положить файл cookies.txt рядом с ботом)
COOKIES_FILE = "cookies.txt"

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь ссылку на YouTube, чтобы скачать видео.")

# Обработчик сообщений (YouTube ссылки)
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text(f"Скачиваю видео: {url} ...")

    ydl_opts = {
        "format": "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "noplaylist": True,
        "cookies": COOKIES_FILE,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            await update.message.reply_text(f"Видео скачано: {filename}")
    except yt_dlp.utils.DownloadError as e:
        await update.message.reply_text(f"❌ Не удалось скачать видео: {str(e)}")

async def main():
    # Создаём приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    # nest_asyncio нужен для работы в некоторых средах (Render)
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())

