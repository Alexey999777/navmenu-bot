# main.py
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import user_handlers, admin_handlers
from middlewares.antiflood import DropOldMessagesMiddleware


async def main():
    # Инициализация базы данных
    await init_db()

    # Создание бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем middleware для фильтрации старых сообщений
    dp.message.middleware(DropOldMessagesMiddleware())
    dp.callback_query.middleware(DropOldMessagesMiddleware())

    # Подключаем роутеры
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    print("🚀 Бот запущен. Ожидаем сообщений...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())