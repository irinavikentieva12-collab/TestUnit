import asyncpg
from typing import Optional, List
from datetime import datetime
from config import settings
from .models import UserInteraction, PriceAlert, UserSubscription


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            min_size=1,
            max_size=10
        )
        await self.create_tables()
    
    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
    
    async def create_tables(self):
        async with self.pool.acquire() as conn:
            # User interactions table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    username VARCHAR(255),
                    request_text TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Price alerts table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    symbol VARCHAR(50) NOT NULL,
                    target_price DECIMAL(20, 8) NOT NULL,
                    alert_type VARCHAR(10) NOT NULL CHECK (alert_type IN ('above', 'below')),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User subscriptions table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    subscription_type VARCHAR(20) NOT NULL CHECK (subscription_type IN ('crypto', 'stocks', 'news')),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, subscription_type)
                )
            ''')
    
    async def save_interaction(self, user_id: int, username: Optional[str], 
                             request_text: str, response_text: str) -> UserInteraction:
        """Сохранение взаимодействия пользователя"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                INSERT INTO user_interactions (user_id, username, request_text, response_text)
                VALUES ($1, $2, $3, $4)
                RETURNING id, user_id, username, request_text, response_text, created_at
            ''', user_id, username, request_text, response_text)
            
            return UserInteraction(
                id=row['id'],
                user_id=row['user_id'],
                username=row['username'],
                request_text=row['request_text'],
                response_text=row['response_text'],
                created_at=row['created_at']
            )
    
    async def get_user_interactions(self, user_id: int, limit: int = 10) -> List[UserInteraction]:
        """Получение истории взаимодействий пользователя"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, user_id, username, request_text, response_text, created_at
                FROM user_interactions
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            ''', user_id, limit)
            
            return [
                UserInteraction(
                    id=row['id'],
                    user_id=row['user_id'],
                    username=row['username'],
                    request_text=row['request_text'],
                    response_text=row['response_text'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
    
    async def add_price_alert(self, user_id: int, symbol: str, 
                            target_price: float, alert_type: str) -> PriceAlert:
        """Добавление ценового алерта"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                INSERT INTO price_alerts (user_id, symbol, target_price, alert_type)
                VALUES ($1, $2, $3, $4)
                RETURNING id, user_id, symbol, target_price, alert_type, is_active, created_at
            ''', user_id, symbol, target_price, alert_type)
            
            return PriceAlert(
                id=row['id'],
                user_id=row['user_id'],
                symbol=row['symbol'],
                target_price=float(row['target_price']),
                alert_type=row['alert_type'],
                is_active=row['is_active'],
                created_at=row['created_at']
            )
    
    async def get_user_alerts(self, user_id: int) -> List[PriceAlert]:
        """Получение алертов пользователя"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, user_id, symbol, target_price, alert_type, is_active, created_at
                FROM price_alerts
                WHERE user_id = $1 AND is_active = TRUE
                ORDER BY created_at DESC
            ''', user_id)
            
            return [
                PriceAlert(
                    id=row['id'],
                    user_id=row['user_id'],
                    symbol=row['symbol'],
                    target_price=float(row['target_price']),
                    alert_type=row['alert_type'],
                    is_active=row['is_active'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
    
    async def toggle_subscription(self, user_id: int, subscription_type: str) -> UserSubscription:
        """Переключение подписки пользователя"""
        async with self.pool.acquire() as conn:
            # Проверяем существующую подписку
            existing = await conn.fetchrow('''
                SELECT id, user_id, subscription_type, is_active, created_at
                FROM user_subscriptions
                WHERE user_id = $1 AND subscription_type = $2
            ''', user_id, subscription_type)
            
            if existing:
                # Обновляем существующую подписку
                is_active = not existing['is_active']
                row = await conn.fetchrow('''
                    UPDATE user_subscriptions
                    SET is_active = $1
                    WHERE user_id = $2 AND subscription_type = $3
                    RETURNING id, user_id, subscription_type, is_active, created_at
                ''', is_active, user_id, subscription_type)
            else:
                # Создаем новую подписку
                row = await conn.fetchrow('''
                    INSERT INTO user_subscriptions (user_id, subscription_type, is_active)
                    VALUES ($1, $2, TRUE)
                    RETURNING id, user_id, subscription_type, is_active, created_at
                ''', user_id, subscription_type)
            
            return UserSubscription(
                id=row['id'],
                user_id=row['user_id'],
                subscription_type=row['subscription_type'],
                is_active=row['is_active'],
                created_at=row['created_at']
            )
    
    async def get_user_subscriptions(self, user_id: int) -> List[UserSubscription]:
        """Получение подписок пользователя"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, user_id, subscription_type, is_active, created_at
                FROM user_subscriptions
                WHERE user_id = $1
                ORDER BY created_at DESC
            ''', user_id)
            
            return [
                UserSubscription(
                    id=row['id'],
                    user_id=row['user_id'],
                    subscription_type=row['subscription_type'],
                    is_active=row['is_active'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
    
    async def delete_price_alert(self, alert_id: int, user_id: int) -> bool:
        """Удаление ценового алерта"""
        async with self.pool.acquire() as conn:
            result = await conn.execute('''
                DELETE FROM price_alerts
                WHERE id = $1 AND user_id = $2
            ''', alert_id, user_id)
            
            return result == "DELETE 1"


# Глобальный экземпляр базы данных
db = Database()
