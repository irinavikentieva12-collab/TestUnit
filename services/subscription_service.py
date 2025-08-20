import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database.connection import db
from services.finance_api import finance_api


class SubscriptionService:
    def __init__(self):
        self.is_running = False
        self.task = None
    
    async def start_subscription_service(self):
        """Запуск сервиса подписок"""
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self._subscription_loop())
            print("Subscription service started")
    
    async def stop_subscription_service(self):
        """Остановка сервиса подписок"""
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            print("Subscription service stopped")
    
    async def _subscription_loop(self):
        """Основной цикл сервиса подписок"""
        while self.is_running:
            try:
                await self._process_subscriptions()
                await asyncio.sleep(300)  # Проверка каждые 5 минут
            except Exception as e:
                print(f"Error in subscription loop: {e}")
                await asyncio.sleep(60)  # Пауза при ошибке
    
    async def _process_subscriptions(self):
        """Обработка активных подписок"""
        # Получаем всех пользователей с активными подписками
        subscriptions = await self._get_all_active_subscriptions()
        
        for sub in subscriptions:
            try:
                if sub.subscription_type == 'crypto':
                    await self._send_crypto_update(sub.user_id)
                elif sub.subscription_type == 'stocks':
                    await self._send_stocks_update(sub.user_id)
                elif sub.subscription_type == 'news':
                    await self._send_news_update(sub.user_id)
            except Exception as e:
                print(f"Error processing subscription for user {sub.user_id}: {e}")
    
    async def _get_all_active_subscriptions(self):
        """Получение всех активных подписок"""
        # Здесь должна быть логика получения подписок из БД
        # Пока возвращаем пустой список
        return []
    
    async def _send_crypto_update(self, user_id: int):
        """Отправка обновления по криптовалютам"""
        # Получаем трендовые криптовалюты
        trending = await finance_api.get_trending_cryptos()
        
        if trending:
            message = "🔥 Обновление по криптовалютам:\n\n"
            for i, coin in enumerate(trending[:5], 1):
                message += f"{i}. {coin['name']} ({coin['symbol']})\n"
                if coin['market_cap_rank']:
                    message += f"   Ранг: #{coin['market_cap_rank']}\n"
                message += f"   Цена в BTC: {coin['price_btc']:.8f}\n\n"
            
            message += "💡 Используйте /trending для получения полного списка"
            
            # Здесь должна быть отправка сообщения пользователю
            print(f"Would send crypto update to user {user_id}: {message[:100]}...")
    
    async def _send_stocks_update(self, user_id: int):
        """Отправка обновления по акциям"""
        # Эмуляция данных по акциям
        stocks_data = [
            {"symbol": "AAPL", "change": "+2.5%"},
            {"symbol": "GOOGL", "change": "-1.2%"},
            {"symbol": "TSLA", "change": "+5.8%"},
            {"symbol": "MSFT", "change": "+0.9%"},
            {"symbol": "AMZN", "change": "-0.7%"}
        ]
        
        message = "📈 Обновление по акциям:\n\n"
        for stock in stocks_data:
            emoji = "📈" if stock['change'].startswith('+') else "📉"
            message += f"{emoji} {stock['symbol']}: {stock['change']}\n"
        
        message += "\n💡 Используйте /price <символ> для получения подробной информации"
        
        # Здесь должна быть отправка сообщения пользователю
        print(f"Would send stocks update to user {user_id}: {message[:100]}...")
    
    async def _send_news_update(self, user_id: int):
        """Отправка финансовых новостей"""
        # Эмуляция финансовых новостей
        news_items = [
            "📰 Bitcoin достиг нового максимума года",
            "🏦 Федеральная резервная система объявила о новых ставках",
            "💼 Tesla представила новый план развития",
            "🌍 Европейский центральный банк обновил прогнозы",
            "📊 Рынок криптовалют показал рекордный объем торгов"
        ]
        
        message = "📰 Финансовые новости:\n\n"
        for i, news in enumerate(news_items, 1):
            message += f"{i}. {news}\n"
        
        message += "\n💡 Оставайтесь в курсе событий!"
        
        # Здесь должна быть отправка сообщения пользователю
        print(f"Would send news update to user {user_id}: {message[:100]}...")
    
    async def send_welcome_message(self, user_id: int, subscription_type: str):
        """Отправка приветственного сообщения при подписке"""
        messages = {
            'crypto': "🎉 Добро пожаловать в мир криптовалют!\n\nВы будете получать регулярные обновления о трендовых монетах и важных событиях на крипторынке.",
            'stocks': "📈 Добро пожаловать в мир акций!\n\nВы будете получать регулярные обновления о движении акций и важных событиях на фондовом рынке.",
            'news': "📰 Добро пожаловать в мир финансовых новостей!\n\nВы будете получать регулярные обновления о важных событиях в мире финансов."
        }
        
        message = messages.get(subscription_type, "Добро пожаловать!")
        message += "\n\n💡 Используйте /subscriptions для управления подписками"
        
        # Здесь должна быть отправка сообщения пользователю
        print(f"Would send welcome message to user {user_id}: {message}")
    
    async def send_price_alert(self, user_id: int, symbol: str, current_price: float, target_price: float, alert_type: str):
        """Отправка ценового алерта"""
        emoji = "📈" if alert_type == "above" else "📉"
        direction = "выше" if alert_type == "above" else "ниже"
        
        message = f"""
🔔 Ценовой алерт!

{emoji} {symbol.upper()} достиг целевой цены!

💵 Текущая цена: ${current_price:,.2f}
🎯 Целевая цена: ${target_price:,.2f}
📊 Тип алерта: {direction} цены

💡 Используйте /alerts для управления алертами
        """
        
        # Здесь должна быть отправка сообщения пользователю
        print(f"Would send price alert to user {user_id}: {message}")
    
    async def check_price_alerts(self):
        """Проверка и отправка ценовых алертов"""
        # Получаем все активные алерты
        alerts = await self._get_all_active_alerts()
        
        for alert in alerts:
            try:
                # Получаем текущую цену
                current_price = await self._get_current_price(alert.symbol)
                
                if current_price is not None:
                    should_trigger = False
                    
                    if alert.alert_type == "above" and current_price >= alert.target_price:
                        should_trigger = True
                    elif alert.alert_type == "below" and current_price <= alert.target_price:
                        should_trigger = True
                    
                    if should_trigger:
                        await self.send_price_alert(
                            alert.user_id,
                            alert.symbol,
                            current_price,
                            alert.target_price,
                            alert.alert_type
                        )
                        # Деактивируем алерт
                        await self._deactivate_alert(alert.id)
                        
            except Exception as e:
                print(f"Error checking alert {alert.id}: {e}")
    
    async def _get_all_active_alerts(self):
        """Получение всех активных алертов"""
        # Здесь должна быть логика получения алертов из БД
        # Пока возвращаем пустой список
        return []
    
    async def _get_current_price(self, symbol: str) -> float:
        """Получение текущей цены актива"""
        try:
            # Пробуем получить цену криптовалюты
            crypto_info = await finance_api.get_crypto_info(symbol.lower())
            if crypto_info:
                return crypto_info['current_price']
            
            # Пробуем получить цену акции
            stock_info = await finance_api.get_stock_price(symbol.upper())
            if stock_info:
                return stock_info['price']
            
            return None
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None
    
    async def _deactivate_alert(self, alert_id: int):
        """Деактивация алерта"""
        # Здесь должна быть логика обновления БД
        print(f"Would deactivate alert {alert_id}")


# Глобальный экземпляр сервиса подписок
subscription_service = SubscriptionService()
