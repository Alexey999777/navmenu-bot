# config.py
import os
from dotenv import load_dotenv

# Загружаем .env только если запускаем локально
if os.path.exists(".env"):
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MAX_CHANNELS = int(os.getenv("MAX_CHANNELS", 3))

# Используем DATABASE_URL напрямую (Railway задаёт его автоматически)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Локальная БД (для разработки)
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "navmenu_bot")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"