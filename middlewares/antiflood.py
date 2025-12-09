# middlewares/antiflood.py
import time
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable


class DropOldMessagesMiddleware(BaseMiddleware):
    """
    Игнорирует сообщения и callback-запросы, отправленные более 30 секунд назад.
    Защищает от выполнения "накопившихся" команд после перезапуска бота.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Обрабатываем только Message и CallbackQuery
        if isinstance(event, (Message, CallbackQuery)):
            current_time = time.time()
            event_time = event.date.timestamp() if isinstance(event, Message) else event.message.date.timestamp()

            # Игнорировать, если событие старше 30 секунд
            if current_time - event_time > 60:
                event_type = "сообщение" if isinstance(event, Message) else "нажатие кнопки"
                user_id = event.from_user.id
                print(
                    f"🚯 Игнорируем устаревшее {event_type} от user_id={user_id} (возраст: {int(current_time - event_time)} сек)")
                return  # не передаём обработчику

        return await handler(event, data)