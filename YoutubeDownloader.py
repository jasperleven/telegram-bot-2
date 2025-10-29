#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import yt_dlp
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Позволяет запускать event loop на Render
nest_asyncio.apply()

# Токен берем из переменных окружения (Render Environment Variables)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Проверяем наличие токена
if not BOT_TOKEN:
    raise ValueError("❌ Не найден BOT_TOKEN. Добавь его в Environment Variables на Render.")

# --- Логика скачивания видео ---
async def download_video(url: str) -> str:
    try:
        os.makedirs("downloads", exist_ok=True)
        output_path = os.path.join("downloads", "%(title)s.%(ext)s")

        # Проверяем, есть ли cookies.txt рядом со скриптом
        cookie_path = "cookies.txt" if os.path.exists("cookies.txt") else None

        ydl_opts = {
            "format": "mp4",
            "outtmpl": output_path,
            "noplaylist": True,
            "geo_bypass": True,
            "quiet": True,
            "cookiefile": cookie_path,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename

    except Exception as e:
        print(f"Ошибка при скачивании: {e}")
        return None


# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Привет! Отправь мне ссылку на YouTube-видео, и я скачаю его для тебя."
    )


# --- Получение ссылок ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("⚠️ Отправь корректную ссылку на видео YouTube.")
        return

    await update.message.reply_text("⏳ Загружаю видео, подожди немного...")

    filepath = await download_video(url)

    if filepath and os.path.exists(filepath):
        await update.message.reply_video(video=open(filepath, "rb"))
        os.remove(filepath)
    else:
        await update.message.reply_text(
            "❌ Не удалось скачать видео. Возможно, YouTube требует авторизацию или видео недоступно."
        )


# --- Основная функция ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен и ожидает сообщения...")
    app.run_polling()


if __name__ == "__main__":
    main()

