# Развертывание

## Требования

- Docker и Docker Compose
- Telegram Bot Token

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd finance-bot
```

2. Настройте переменные окружения:
```bash
cp env.example .env
nano .env
```

Укажите токен бота:
```env
BOT_TOKEN=ваш_токен_здесь
```

3. Запустите:
```bash
docker-compose up -d
```

4. Проверьте работу:
- Найдите бота в Telegram
- Отправьте `/start`

## Управление

Основные команды:

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Логи
docker-compose logs -f bot

# Перезапуск
docker-compose restart bot
```

Отладка:

```bash
# Подключение к контейнеру
docker-compose exec bot bash

# База данных
docker-compose exec postgres psql -U postgres -d finance_bot_db
```

## Устранение проблем

Если бот не отвечает:
```bash
# Проверьте логи
docker-compose logs bot

# Проверьте контейнеры
docker-compose ps
```

Если проблемы с БД:
```bash
# Перезапустите PostgreSQL
docker-compose restart postgres
```