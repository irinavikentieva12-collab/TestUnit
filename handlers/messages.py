from aiogram import Router, F
from aiogram.types import Message
from database.connection import db
from services.finance_api import finance_api
import re

router = Router()


@router.message(F.text)
async def handle_text_message(message: Message):
    """Обработчик всех текстовых сообщений"""
    text = message.text.strip().lower()
    
    # Игнорируем команды
    if text.startswith('/'):
        return
    
    # Поиск криптовалюты или акции
    if len(text) >= 2:
        response = await process_finance_query(text)
    else:
        response = "❌ Введите название криптовалюты или акции (минимум 2 символа).\n\n💡 Или используйте меню для удобной навигации!"
    
    await message.answer(response)
    
    # Сохраняем взаимодействие
    await db.save_interaction(
        user_id=message.from_user.id,
        username=message.from_user.username,
        request_text=message.text,
        response_text=response
    )


async def process_finance_query(query: str) -> str:
    """Обработка финансового запроса"""
    # Сначала пробуем найти точное совпадение для криптовалюты
    crypto_info = await finance_api.get_crypto_info(query)
    
    if crypto_info:
        return format_crypto_response(crypto_info)
    
    # Если не нашли криптовалюту, пробуем акции
    stock_info = await finance_api.get_stock_price(query.upper())
    if stock_info:
        return format_stock_response(stock_info)
    
    # Если не нашли точное совпадение, пробуем поиск
    search_results = await finance_api.search_crypto(query)
    if search_results:
        return format_search_results(search_results, query)
    
    return f"❌ Не удалось найти информацию для '{query}'.\n\n💡 Попробуйте:\n• Используйте меню для навигации\n• Или напишите точное название криптовалюты/акции"


def format_crypto_response(crypto_info: dict) -> str:
    """Форматирование ответа для криптовалюты"""
    change_24h = crypto_info.get('price_change_percentage_24h', 0)
    change_emoji = "📈" if change_24h >= 0 else "📉"
    
    response = f"""
💰 {crypto_info['name']} ({crypto_info['symbol']})

💵 Текущая цена: ${crypto_info['current_price']:,.2f}
{change_emoji} Изменение за 24ч: {change_24h:+.2f}%
📊 Рыночная капитализация: ${crypto_info['market_cap']:,.0f}
📈 Объем торгов (24ч): ${crypto_info['volume_24h']:,.0f}

📝 Описание:
{crypto_info['description']}

💡 Используйте меню "🔔 Алерты" для создания ценового алерта!
    """
    
    return response


def format_stock_response(stock_info: dict) -> str:
    """Форматирование ответа для акций"""
    change = stock_info.get('change', 0)
    change_emoji = "📈" if change >= 0 else "📉"
    
    response = f"""
📈 {stock_info['symbol']}

💵 Текущая цена: ${stock_info['price']:,.2f}
{change_emoji} Изменение: {change:+.2f} ({stock_info['change_percent']})
📊 Объем торгов: {stock_info['volume']:,}
💰 Рыночная капитализация: ${stock_info['market_cap']:,}

💡 Используйте меню "🔔 Алерты" для создания ценового алерта!
    """
    
    return response


def format_search_results(search_results: list, query: str) -> str:
    """Форматирование результатов поиска"""
    response = f"🔍 Результаты поиска для '{query}':\n\n"
    
    for i, coin in enumerate(search_results, 1):
        rank_text = f" (Ранг: #{coin['market_cap_rank']})" if coin['market_cap_rank'] else ""
        response += f"{i}. {coin['name']} ({coin['symbol']}){rank_text}\n"
    
    response += f"\n💡 Напишите точное название для получения подробной информации."
    
    return response


@router.message(F.text.regexp(r"^bitcoin$|^btc$"))
async def handle_bitcoin(message: Message):
    """Специальный обработчик для Bitcoin"""
    crypto_info = await finance_api.get_crypto_info("bitcoin")
    if crypto_info:
        response = f"""
🏆 Bitcoin (BTC) - Король криптовалют

💵 Текущая цена: ${crypto_info['current_price']:,.2f}
📈 Изменение за 24ч: {crypto_info['price_change_percentage_24h']:+.2f}%
📊 Рыночная капитализация: ${crypto_info['market_cap']:,.0f}
📈 Объем торгов (24ч): ${crypto_info['volume_24h']:,.0f}

💎 Доминирование: ~50% рынка
🌐 Первая и самая известная криптовалюта

💡 Используйте меню для:
• Создания алертов по цене
• Просмотра сводки рынка
        """
    else:
        response = "❌ Не удалось получить данные о Bitcoin."
    
    await message.answer(response)
    
    # Сохраняем взаимодействие
    await db.save_interaction(
        user_id=message.from_user.id,
        username=message.from_user.username,
        request_text=message.text,
        response_text=response
    )


@router.message(F.text.regexp(r"^ethereum$|^eth$"))
async def handle_ethereum(message: Message):
    """Специальный обработчик для Ethereum"""
    crypto_info = await finance_api.get_crypto_info("ethereum")
    if crypto_info:
        response = f"""
🔷 Ethereum (ETH) - Платформа смарт-контрактов

💵 Текущая цена: ${crypto_info['current_price']:,.2f}
📈 Изменение за 24ч: {crypto_info['price_change_percentage_24h']:+.2f}%
📊 Рыночная капитализация: ${crypto_info['market_cap']:,.0f}
📈 Объем торгов (24ч): ${crypto_info['volume_24h']:,.0f}

⚡ Основа DeFi и NFT экосистемы
🔗 Поддерживает смарт-контракты

💡 Используйте меню для:
• Создания алертов по цене
• Просмотра трендовых токенов
        """
    else:
        response = "❌ Не удалось получить данные о Ethereum."
    
    await message.answer(response)
    
    # Сохраняем взаимодействие
    await db.save_interaction(
        user_id=message.from_user.id,
        username=message.from_user.username,
        request_text=message.text,
        response_text=response
    )
