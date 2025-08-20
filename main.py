import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database.connection import db
from services.finance_api import finance_api
from services.subscription_service import subscription_service
from handlers import menu, messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Создаем бота
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаемся к БД
    logger.info("Connecting to database...")
    await db.connect()
    
    # Запускаем сервис подписок  
    await subscription_service.start_subscription_service()
    
    # Подключаем обработчики
    dp.include_router(menu.router)
    dp.include_router(messages.router)
    
    @dp.error()
    async def error_handler(update, exception):
        logger.error(f"Error: {exception}")
        return True
    
    # Запускаем бота
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    finally:
        await subscription_service.stop_subscription_service()
        await db.close()
        await finance_api.close_sessions()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
