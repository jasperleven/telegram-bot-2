#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли ссылку на YouTube видео, и я попробую его скачать."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("Начинаю скачивание...")
    try:
        ydl_opts = {"outtmpl": "%(title)s.%(ext)s", "noplaylist": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_text("Видео успешно скачано!")
    except yt_dlp.utils.DownloadError:
        await update.message.reply_text(
            "❌ Не удалось скачать видео. Возможно, требуется авторизация или видео недоступно."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Бот запущен...")
    app.run_polling()  # запускаем без asyncio.run()

if __name__ == "__main__":
    main()

