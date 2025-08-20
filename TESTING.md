# Тестирование

## Запуск бота

```bash
# Запустите приложение
docker-compose up -d

# Проверьте логи
docker-compose logs -f bot
```

## Тестирование команд

Найдите бота в Telegram и протестируйте:

### Основные команды
- `/start` - Приветствие
- `/help` - Справка
- `/price bitcoin` - Цена Bitcoin
- `/trending` - Трендовые криптовалюты
- `/market` - Сводка рынка

### Текстовые запросы
Просто напишите:
- `bitcoin`
- `ethereum` 
- `AAPL`
- `GOOGL`

### Алерты и подписки
- `/alerts` - Просмотр алертов
- `/alert_add` - Добавить алерт
- `/subscriptions` - Подписки

## Проверка базы данных

```bash
# Подключитесь к БД
docker-compose exec postgres psql -U postgres -d finance_bot_db

# Посмотрите таблицы
\dt

# Проверьте записи
SELECT COUNT(*) FROM user_interactions;
```

## Если что-то не работает

```bash
# Проверьте логи
docker-compose logs bot

# Проверьте статус контейнеров
docker-compose ps

# Перезапустите
docker-compose restart bot
```

## API тесты

Проверьте доступность API:

```bash
# CoinGecko
curl "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

# Должен вернуть цену Bitcoin
```