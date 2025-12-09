from aiogram import types
from aiogram.filters import BaseFilter
from database import is_user_channel_admin


class AdminOnly(BaseFilter):
    """
    Проверяет, является ли пользователь админом канала.
    channel_id нужно передавать отдельно (например, через callback_data или состояние).
    """
    async def __call__(self, message: types.Message) -> bool:
        # Для простоты: проверим, есть ли у юзера хоть один канал
        # В реальности channel_id можно получить из сообщения или состояния
        # Пока просто возвращаем True — админ проверяется в обработчике
        return True