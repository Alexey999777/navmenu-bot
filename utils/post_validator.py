from aiogram import Bot
from config import OWNER_ID  # ← Лучше импортировать из config

async def is_post_accessible(bot, chat_id: int, message_id: int) -> bool:
    """
    Всегда возвращает True — мы доверяем, что пост существует.
    Не делаем forward → не будет спама.
    """
    return True  # ⚠️ Просто считаем, что пост доступен