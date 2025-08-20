#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы бота с меню
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database.connection import db
from services.finance_api import finance_api
from handlers import menu, messages

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_bot():
    """Тестирование бота"""
    print("🚀 Запуск тестирования бота...")
    
    try:
        # Создаем бота
        bot = Bot(token=settings.bot_token)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Подключаемся к БД
        print("📊 Подключение к базе данных...")
        await db.connect()
        
        # Подключаем обработчики
        dp.include_router(menu.router)
        dp.include_router(messages.router)
        
        print("✅ Бот успешно настроен!")
        print("📱 Теперь можно запускать бота через main.py")
        
        # Закрываем соединения
        await db.close()
        await finance_api.close_sessions()
        await bot.session.close()
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_bot())
    if success:
        print("🎉 Тестирование завершено успешно!")
    else:
        print("💥 Тестирование завершено с ошибками!")
