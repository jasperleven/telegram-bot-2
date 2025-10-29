#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"  # вставьте сюда токен

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь ссылку на YouTube, и я попробую скачать видео."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("Пробую скачать видео...")

    ydl_opts = {
        "format": "best",
        "outtmpl": "%(title)s.%(ext)s",  # сохраняем в текущей папке
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Видео')
            await update.message.reply_text(f"Видео '{title}' успешно скачано!")
    except yt_dlp.utils.DownloadError as e:
        logging.error(e)
        await update.message.reply_text(
            "❌ Не удалось скачать видео. Возможно, оно недоступно или защищено авторскими правами."
        )
    except Exception as e:
        logging.error(e)
        await update.message.reply_text(f"Произошла ошибка: {e}")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Хэндлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_video))

    # Запуск бота
    logging.info("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    # Используем nest_asyncio для Render/сред с уже запущенным loop
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())

