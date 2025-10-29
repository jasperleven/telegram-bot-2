#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

# ==============================
# Настройки
# ==============================
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # задается в Environment Variables на Render
DOWNLOAD_DIR = "downloads"
COOKIES_FILE = "cookies.txt"  # файл cookies для авторизации YouTube (если нужно)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ==============================
# Функции бота
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь ссылку на видео YouTube для скачивания.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Неверная ссылка.")
        return

    await update.message.reply_text("⏳ Начинаю скачивание...")

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
    }

    # Использовать cookies, если нужно для видео с ограничением
    if os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_text(f"✅ Видео скачано: {os.path.basename(filename)}")
    except yt_dlp.utils.DownloadError as e:
        await update.message.reply_text("❌ Не удалось скачать видео. Возможно, требуется авторизация или видео недоступно.")
        print("YT-DLP Error:", e)

# ==============================
# Запуск бота
# ==============================
async def main():
    # Сбрасываем webhook на всякий случай
    bot = Bot(BOT_TOKEN)
    await bot.delete_webhook()
    print("Webhook сброшен, можно использовать polling.")

    # Создаем приложение и регистрируем обработчики
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))  # help делает то же, что start
    app.add_handler(CommandHandler("download", download_video))
    app.add_handler(CommandHandler("yt", download_video))  # альтернатива /yt для скачивания
    app.add_handler(CommandHandler("video", download_video))  # альтернатива /video

    # Обработчик текста (ссылки без команды)
    app.add_handler(app.builder.message_handler(download_video))

    print("Бот запущен. Ожидание сообщений...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

