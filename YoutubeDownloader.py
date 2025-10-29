#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли ссылку на YouTube видео, и я попробую его скачать."
    )

# Основная функция скачивания видео
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("Начинаю скачивание...")
    try:
        # Настройки yt-dlp
        ydl_opts = {
            "outtmpl": "%(title)s.%(ext)s",
            "noplaylist": True,
        }
        # Скачиваем видео
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_text("Видео успешно скачано!")
    except yt_dlp.utils.DownloadError as e:
        await update.message.reply_text(
            "❌ Не удалось скачать видео. Возможно, требуется авторизация или видео недоступно."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# Основная асинхронная функция
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем хэндлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

