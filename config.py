# config.py
import os

# Обязательные переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MAX_CHANNELS = int(os.getenv("MAX_CHANNELS", "3"))

# Используем ТОЛЬКО DATABASE_URL от Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL не задан. Добавьте PostgreSQL в Railway.")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не задан.")