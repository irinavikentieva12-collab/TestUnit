-- Инициализация базы данных для Finance Bot
-- Создание таблиц и индексов

-- Таблица для истории взаимодействий пользователей
CREATE TABLE IF NOT EXISTS user_interactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username VARCHAR(255),
    request_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для быстрого поиска по пользователю
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_created_at ON user_interactions(created_at);

-- Таблица для ценовых алертов
CREATE TABLE IF NOT EXISTS price_alerts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    target_price DECIMAL(20, 8) NOT NULL,
    alert_type VARCHAR(10) NOT NULL CHECK (alert_type IN ('above', 'below')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для алертов
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_symbol ON price_alerts(symbol);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts(is_active);

-- Таблица для подписок пользователей
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    subscription_type VARCHAR(20) NOT NULL CHECK (subscription_type IN ('crypto', 'stocks', 'news')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, subscription_type)
);

-- Индексы для подписок
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_type ON user_subscriptions(subscription_type);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_active ON user_subscriptions(is_active);

-- Создание представления для статистики
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    user_id,
    COUNT(*) as total_interactions,
    COUNT(DISTINCT DATE(created_at)) as active_days,
    MIN(created_at) as first_interaction,
    MAX(created_at) as last_interaction
FROM user_interactions
GROUP BY user_id;

-- Создание представления для активных алертов
CREATE OR REPLACE VIEW active_alerts AS
SELECT 
    pa.*,
    ui.username
FROM price_alerts pa
LEFT JOIN user_interactions ui ON pa.user_id = ui.user_id
WHERE pa.is_active = TRUE
ORDER BY pa.created_at DESC;

-- Комментарии к таблицам
COMMENT ON TABLE user_interactions IS 'История взаимодействий пользователей с ботом';
COMMENT ON TABLE price_alerts IS 'Ценовые алерты пользователей';
COMMENT ON TABLE user_subscriptions IS 'Подписки пользователей на обновления';
COMMENT ON VIEW user_stats IS 'Статистика использования бота по пользователям';
COMMENT ON VIEW active_alerts IS 'Активные ценовые алерты с информацией о пользователях';
