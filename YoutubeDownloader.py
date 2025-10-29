#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import yt_dlp
import nest_asyncio
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Разрешаем asyncio работать в Render
nest_asyncio.apply()

# Берем токен из переменных окружения Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне ссылку на YouTube, и я скачаю видео для тебя 🎬")

# Обработка ссылок YouTube
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("❌ Это не ссылка на YouTube.")
        return

    await update.message.reply_text("⏳ Скачиваю видео, подожди немного...")

    ydl_opts = {
        "outtmpl": "video.%(ext)s",
        "format": "mp4",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(filename, "rb"))
        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при скачивании: {e}")

# Основная функция запуска
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    await app.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook сброшен, бот запущен в режиме polling.")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())


# In[ ]:




