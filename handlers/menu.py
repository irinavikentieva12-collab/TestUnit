from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.connection import db
from services.finance_api import finance_api
import re

router = Router()


class AlertStates(StatesGroup):
    waiting_for_symbol = State()
    waiting_for_price = State()
    waiting_for_type = State()


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Цены криптовалют", callback_data="menu_crypto")
    builder.button(text="📈 Цены акций", callback_data="menu_stocks")
    builder.button(text="🔥 Трендовые монеты", callback_data="menu_trending")
    builder.button(text="📊 Обзор рынка", callback_data="menu_market")
    builder.button(text="🔔 Алерты", callback_data="menu_alerts")
    builder.button(text="📰 Подписки", callback_data="menu_subscriptions")
    builder.button(text="📚 История", callback_data="menu_history")
    builder.button(text="❓ Помощь", callback_data="menu_help")
    builder.adjust(2)
    return builder.as_markup()


def get_crypto_menu() -> InlineKeyboardMarkup:
    """Меню криптовалют"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Bitcoin", callback_data="crypto_bitcoin")
    builder.button(text="Ethereum", callback_data="crypto_ethereum")
    builder.button(text="Binance Coin", callback_data="crypto_binancecoin")
    builder.button(text="Solana", callback_data="crypto_solana")
    builder.button(text="Cardano", callback_data="crypto_cardano")
    builder.button(text="🔍 Поиск", callback_data="crypto_search")
    builder.button(text="⬅️ Назад", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()


def get_stocks_menu() -> InlineKeyboardMarkup:
    """Меню акций"""
    builder = InlineKeyboardBuilder()
    builder.button(text="AAPL (Apple)", callback_data="stock_AAPL")
    builder.button(text="GOOGL (Google)", callback_data="stock_GOOGL")
    builder.button(text="TSLA (Tesla)", callback_data="stock_TSLA")
    builder.button(text="MSFT (Microsoft)", callback_data="stock_MSFT")
    builder.button(text="AMZN (Amazon)", callback_data="stock_AMZN")
    builder.button(text="🔍 Поиск", callback_data="stock_search")
    builder.button(text="⬅️ Назад", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()


def get_alerts_menu() -> InlineKeyboardMarkup:
    """Меню алертов"""
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить алерт", callback_data="alert_add")
    builder.button(text="📋 Мои алерты", callback_data="alert_list")
    builder.button(text="🗑 Удалить алерт", callback_data="alert_remove")
    builder.button(text="⬅️ Назад", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()


def get_subscriptions_menu() -> InlineKeyboardMarkup:
    """Меню подписок"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📰 Криптовалюты", callback_data="sub_crypto")
    builder.button(text="📈 Акции", callback_data="sub_stocks")
    builder.button(text="📊 Новости", callback_data="sub_news")
    builder.button(text="⬅️ Назад", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    welcome_text = """Привет! Это Finance Bot.

Получай актуальные цены криптовалют и акций через удобное меню.

Выберите нужный раздел:"""
    
    await message.answer(welcome_text, reply_markup=get_main_menu())
    
    await db.save_interaction(
        user_id=message.from_user.id,
        username=message.from_user.username,
        request_text="/start",
        response_text="Welcome message"
    )


@router.callback_query(F.data == "menu_main")
async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню"""
    await callback.message.edit_text(
        "Выберите нужный раздел:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_crypto")
async def show_crypto_menu(callback: CallbackQuery):
    """Показать меню криптовалют"""
    await callback.message.edit_text(
        "💰 Выберите криптовалюту:",
        reply_markup=get_crypto_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_stocks")
async def show_stocks_menu(callback: CallbackQuery):
    """Показать меню акций"""
    await callback.message.edit_text(
        "📈 Выберите акцию:",
        reply_markup=get_stocks_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_trending")
async def show_trending(callback: CallbackQuery):
    """Показать трендовые криптовалюты"""
    trending = await finance_api.get_trending_cryptos()
    
    if trending:
        response = "🔥 Топ криптовалют:\n\n"
        for i, coin in enumerate(trending[:5], 1):
            rank = f"#{coin['market_cap_rank']}" if coin['market_cap_rank'] else ""
            response += f"{i}. {coin['name']} ({coin['symbol']}) {rank}\n"
    else:
        response = "Не удалось получить данные"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="menu_main")
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await callback.answer()
    
    await db.save_interaction(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        request_text="trending",
        response_text=response
    )


@router.callback_query(F.data == "menu_market")
async def show_market(callback: CallbackQuery):
    """Показать обзор рынка"""
    market_data = await finance_api.get_market_summary()
    
    if market_data:
        response = f"""📊 Сводка крипторынка

💰 Общая капитализация: ${market_data['total_market_cap']:,.0f}
📈 Общий объем (24ч): ${market_data['total_volume']:,.0f}
📊 Изменение капитализации (24ч): {market_data['market_cap_change_24h']:.2f}%
🪙 Активных криптовалют: {market_data['active_cryptocurrencies']:,}

🏆 Топ-5 по капитализации:
"""
        # Добавляем топ-5 криптовалют
        top_coins = ['bitcoin', 'ethereum', 'binancecoin', 'solana', 'cardano']
        for coin_id in top_coins:
            coin_info = await finance_api.get_crypto_price(coin_id)
            if coin_info:
                response += f"• {coin_id.title()}: ${coin_info['price']:,.2f}\n"
    else:
        response = "❌ Не удалось получить данные рынка."
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="menu_main")
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await callback.answer()
    
    await db.save_interaction(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        request_text="market",
        response_text=response
    )


@router.callback_query(F.data == "menu_alerts")
async def show_alerts_menu(callback: CallbackQuery):
    """Показать меню алертов"""
    await callback.message.edit_text(
        "🔔 Управление ценовыми алертами:",
        reply_markup=get_alerts_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_subscriptions")
async def show_subscriptions_menu(callback: CallbackQuery):
    """Показать меню подписок"""
    subscriptions = await db.get_user_subscriptions(callback.from_user.id)
    
    response = "📰 Ваши подписки:\n\n"
    
    # Определяем статус каждой подписки
    sub_types = {
        'crypto': 'Криптовалюты',
        'stocks': 'Акции',
        'news': 'Новости'
    }
    
    for sub_type, name in sub_types.items():
        sub = next((s for s in subscriptions if s.subscription_type == sub_type), None)
        status = "✅ Подписан" if sub and sub.is_active else "❌ Не подписан"
        response += f"{name}: {status}\n"
    
    await callback.message.edit_text(response, reply_markup=get_subscriptions_menu())
    await callback.answer()


@router.callback_query(F.data == "menu_history")
async def show_history(callback: CallbackQuery):
    """Показать историю запросов"""
    interactions = await db.get_user_interactions(callback.from_user.id, limit=5)
    
    if interactions:
        response = "📚 Ваша история запросов (последние 5):\n\n"
        for i, interaction in enumerate(interactions, 1):
            response += f"{i}. {interaction.request_text}\n"
            response += f"   📅 {interaction.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    else:
        response = "📚 История запросов пуста."
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="menu_main")
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await callback.answer()
    
    await db.save_interaction(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        request_text="history",
        response_text="История запросов"
    )


@router.callback_query(F.data == "menu_help")
async def show_help(callback: CallbackQuery):
    """Показать справку"""
    help_text = """❓ Справка по боту:

💰 Цены криптовалют - актуальные цены популярных криптовалют
📈 Цены акций - котировки акций крупных компаний
🔥 Трендовые монеты - топ криптовалют по популярности
📊 Обзор рынка - общая статистика крипторынка
🔔 Алерты - настройка ценовых уведомлений
📰 Подписки - подписка на обновления
📚 История - ваши последние запросы

Для поиска конкретной криптовалюты или акции используйте кнопку "🔍 Поиск" в соответствующих разделах."""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="menu_main")
    
    await callback.message.edit_text(help_text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("crypto_"))
async def handle_crypto_selection(callback: CallbackQuery):
    """Обработка выбора криптовалюты"""
    symbol = callback.data.split("_")[1]
    
    crypto_info = await finance_api.get_crypto_info(symbol)
    
    if crypto_info:
        price_change = crypto_info['price_change_percentage_24h']
        change_emoji = "📈" if price_change >= 0 else "📉"
        response = f"""💰 {crypto_info['name']} ({crypto_info['symbol']})

Цена: ${crypto_info['current_price']:,.2f}
{change_emoji} За 24ч: {price_change:+.2f}%
Капитализация: ${crypto_info['market_cap']:,.0f}
Объем: ${crypto_info['volume_24h']:,.0f}"""
    else:
        response = f"Не удалось получить данные для {symbol}"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад к криптовалютам", callback_data="menu_crypto")
    builder.button(text="🏠 Главное меню", callback_data="menu_main")
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await callback.answer()
    
    await db.save_interaction(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        request_text=f"crypto_{symbol}",
        response_text=response
    )


@router.callback_query(F.data.startswith("stock_"))
async def handle_stock_selection(callback: CallbackQuery):
    """Обработка выбора акции"""
    symbol = callback.data.split("_")[1]
    
    stock_info = await finance_api.get_stock_price(symbol)
    
    if stock_info:
        response = f"""📈 {stock_info['symbol']}

Цена: ${stock_info['price']:,.2f}
Изменение: {stock_info['change']:+.2f} ({stock_info['change_percent']})
Объем: {stock_info['volume']:,}"""
    else:
        response = f"Не удалось получить данные для {symbol}"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад к акциям", callback_data="menu_stocks")
    builder.button(text="🏠 Главное меню", callback_data="menu_main")
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await callback.answer()
    
    await db.save_interaction(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        request_text=f"stock_{symbol}",
        response_text=response
    )


@router.callback_query(F.data == "crypto_search")
async def crypto_search_prompt(callback: CallbackQuery, state: FSMContext):
    """Запрос на поиск криптовалюты"""
    await state.set_state(AlertStates.waiting_for_symbol)
    await state.update_data(search_type="crypto")
    
    await callback.message.edit_text(
        "Введите символ криптовалюты (например: bitcoin, ethereum):"
    )
    await callback.answer()


@router.callback_query(F.data == "stock_search")
async def stock_search_prompt(callback: CallbackQuery, state: FSMContext):
    """Запрос на поиск акции"""
    await state.set_state(AlertStates.waiting_for_symbol)
    await state.update_data(search_type="stock")
    
    await callback.message.edit_text(
        "Введите символ акции (например: AAPL, GOOGL):"
    )
    await callback.answer()


@router.message(AlertStates.waiting_for_symbol)
async def process_symbol_input(message: Message, state: FSMContext):
    """Обработка ввода символа (поиск или алерт)"""
    data = await state.get_data()
    search_type = data.get("search_type")
    alert_mode = data.get("alert_mode")
    symbol = message.text.lower().strip()
    
    # Если это режим алерта
    if alert_mode:
        # Проверяем существование символа
        crypto_info = await finance_api.get_crypto_info(symbol)
        if not crypto_info:
            stock_info = await finance_api.get_stock_price(symbol.upper())
            if not stock_info:
                await message.answer(f"❌ Символ '{symbol}' не найден. Попробуйте другой символ.")
                return
        
        await state.update_data(symbol=symbol)
        await state.set_state(AlertStates.waiting_for_price)
        await message.answer(f"Введите целевую цену для {symbol.upper()} (например: 50000):")
        return
    
    # Если это режим поиска
    if search_type == "crypto":
        info = await finance_api.get_crypto_info(symbol)
        if info:
            price_change = info['price_change_percentage_24h']
            change_emoji = "📈" if price_change >= 0 else "📉"
            response = f"""💰 {info['name']} ({info['symbol']})

Цена: ${info['current_price']:,.2f}
{change_emoji} За 24ч: {price_change:+.2f}%
Капитализация: ${info['market_cap']:,.0f}
Объем: ${info['volume_24h']:,.0f}"""
        else:
            response = f"❌ Криптовалюта '{symbol}' не найдена"
    else:
        info = await finance_api.get_stock_price(symbol.upper())
        if info:
            response = f"""📈 {info['symbol']}

Цена: ${info['price']:,.2f}
Изменение: {info['change']:+.2f} ({info['change_percent']})
Объем: {info['volume']:,}"""
        else:
            response = f"❌ Акция '{symbol.upper()}' не найдена"
    
    builder = InlineKeyboardBuilder()
    if search_type == "crypto":
        builder.button(text="⬅️ Назад к криптовалютам", callback_data="menu_crypto")
    else:
        builder.button(text="⬅️ Назад к акциям", callback_data="menu_stocks")
    builder.button(text="🏠 Главное меню", callback_data="menu_main")
    
    await message.answer(response, reply_markup=builder.as_markup())
    await state.clear()
    
    await db.save_interaction(
        user_id=message.from_user.id,
        username=message.from_user.username,
        request_text=f"search_{symbol}",
        response_text=response
    )


# Обработчики алертов
@router.callback_query(F.data == "alert_add")
async def alert_add_prompt(callback: CallbackQuery, state: FSMContext):
    """Запрос на добавление алерта"""
    await state.set_state(AlertStates.waiting_for_symbol)
    await state.update_data(alert_mode=True)
    
    await callback.message.edit_text(
        "Введите символ криптовалюты или акции (например: bitcoin):"
    )
    await callback.answer()


@router.callback_query(F.data == "alert_list")
async def alert_list_show(callback: CallbackQuery):
    """Показать список алертов"""
    alerts = await db.get_user_alerts(callback.from_user.id)
    
    if alerts:
        response = "🔔 Ваши ценовые алерты:\n\n"
        for alert in alerts:
            status = "✅ Активен" if alert.is_active else "❌ Неактивен"
            response += f"ID: {alert.id}\n"
            response += f"Символ: {alert.symbol.upper()}\n"
            response += f"Целевая цена: ${alert.target_price:,.2f}\n"
            response += f"Тип: {alert.alert_type}\n"
            response += f"Статус: {status}\n\n"
    else:
        response = "🔔 У вас пока нет ценовых алертов."
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад к алертам", callback_data="menu_alerts")
    builder.button(text="🏠 Главное меню", callback_data="menu_main")
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "alert_remove")
async def alert_remove_prompt(callback: CallbackQuery):
    """Запрос на удаление алерта"""
    alerts = await db.get_user_alerts(callback.from_user.id)
    
    if not alerts:
        response = "🔔 У вас нет алертов для удаления."
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Назад к алертам", callback_data="menu_alerts")
        builder.button(text="🏠 Главное меню", callback_data="menu_main")
        await callback.message.edit_text(response, reply_markup=builder.as_markup())
        await callback.answer()
        return
    
    response = "🗑 Выберите алерт для удаления:\n\n"
    builder = InlineKeyboardBuilder()
    
    for alert in alerts:
        builder.button(
            text=f"{alert.symbol.upper()} - ${alert.target_price:,.2f}",
            callback_data=f"delete_alert_{alert.id}"
        )
    
    builder.button(text="⬅️ Назад к алертам", callback_data="menu_alerts")
    builder.button(text="🏠 Главное меню", callback_data="menu_main")
    builder.adjust(1)
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("delete_alert_"))
async def delete_alert(callback: CallbackQuery):
    """Удаление алерта"""
    alert_id = int(callback.data.split("_")[2])
    
    success = await db.delete_price_alert(alert_id, callback.from_user.id)
    
    if success:
        response = "✅ Алерт успешно удален!"
    else:
        response = "❌ Не удалось удалить алерт."
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад к алертам", callback_data="menu_alerts")
    builder.button(text="🏠 Главное меню", callback_data="menu_main")
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await callback.answer()


# Обработчики подписок
@router.callback_query(F.data.startswith("sub_"))
async def process_subscription_toggle(callback: CallbackQuery):
    """Обработка переключения подписки"""
    sub_type = callback.data.split("_")[1]  # crypto, stocks, news
    
    subscription = await db.toggle_subscription(
        user_id=callback.from_user.id,
        subscription_type=sub_type
    )
    
    sub_names = {
        'crypto': 'Криптовалюты',
        'stocks': 'Акции',
        'news': 'Новости'
    }
    
    status = "✅ Подписка активирована" if subscription.is_active else "❌ Подписка отключена"
    response = f"{sub_names[sub_type]}: {status}"
    
    await callback.message.answer(response)
    await callback.answer()
    
    # Показываем обновленное меню подписок
    await show_subscriptions_menu(callback)





@router.message(AlertStates.waiting_for_price)
async def process_alert_price(message: Message, state: FSMContext):
    """Обработка цены для алерта"""
    try:
        price = float(message.text.strip())
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
    except ValueError:
        await message.answer("❌ Введите корректную цену (число больше 0).")
        return
    
    await state.update_data(target_price=price)
    await state.set_state(AlertStates.waiting_for_type)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 Выше цены", callback_data="alert_above")
    builder.button(text="📉 Ниже цены", callback_data="alert_below")
    
    await message.answer("Выберите тип алерта:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("alert_"))
async def process_alert_type(callback: CallbackQuery, state: FSMContext):
    """Обработка типа алерта"""
    if callback.data == "alert_add":
        return  # Уже обработано выше
    
    alert_type = callback.data.split("_")[1]  # above или below
    
    data = await state.get_data()
    symbol = data.get("symbol")
    target_price = data.get("target_price")
    
    # Создаем алерт
    alert = await db.add_price_alert(
        user_id=callback.from_user.id,
        symbol=symbol,
        target_price=target_price,
        alert_type=alert_type
    )
    
    alert_type_text = "выше" if alert_type == "above" else "ниже"
    response = f"""✅ Алерт создан!

Символ: {symbol.upper()}
Целевая цена: ${target_price:,.2f}
Тип: {alert_type_text} цены
ID алерта: {alert.id}"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад к алертам", callback_data="menu_alerts")
    builder.button(text="🏠 Главное меню", callback_data="menu_main")
    
    await callback.message.edit_text(response, reply_markup=builder.as_markup())
    await state.clear()
    await callback.answer()
