# 💳 Credits System API

Повнофункціональна система управління кредитами та підписками для AI-генерації документів з підтримкою ідемпотентності, транзакційності та кешування.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Зміст

- [Особливості](#особливості)
- [Архітектура](#архітектура)
- [Встановлення](#встановлення)
- [Швидкий старт](#швидкий-старт)
- [API Endpoints](#api-endpoints)
- [Тарифні плани](#тарифні-плани)
- [Приклади використання](#приклади-використання)
- [Тестування](#тестування)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## ✨ Особливості

### 🔐 Безпека
- ✅ Міжсервісна аутентифікація (Service-to-Service tokens)
- ✅ User аутентифікація (Bearer tokens)
- ✅ Admin аутентифікація
- ✅ CORS підтримка

### 💰 Управління кредитами
- ✅ Автоматичний розрахунок вартості
- ✅ Списання з перевіркою балансу
- ✅ Поповнення балансу
- ✅ Історія транзакцій

### 🔄 Надійність
- ✅ **Ідемпотентність** - захист від подвійного списання
- ✅ **Транзакційність** - atomic операції з БД
- ✅ **Pessimistic locking** - захист від race conditions
- ✅ **Автоматичний rollback** при помилках

### ⚡ Продуктивність
- ✅ Redis кешування балансу (TTL 5 хв)
- ✅ Оптимізовані SQL запити
- ✅ Database connection pooling
- ✅ Асинхронні операції

### 📊 Моніторинг
- ✅ Детальна статистика
- ✅ Логування всіх операцій
- ✅ Health checks
- ✅ Audit trail

---

## 🏗️ Архітектура

### Технологічний стек
```
┌─────────────────────────────────────────┐
│          FastAPI Application            │
├─────────────────────────────────────────┤
│  Internal API  │  Public API  │ Admin  │
├─────────────────────────────────────────┤
│           Services Layer                │
│  CreditService │ SubscriptionService    │
│  TransactionService │ CacheService      │
├─────────────────────────────────────────┤
│         Database Layer                  │
│  SQLAlchemy ORM  │  Alembic Migrations │
├─────────────────────────────────────────┤
│    PostgreSQL    │       Redis         │
└─────────────────────────────────────────┘
```

### Структура проекту
```
credits-system/
├── app/
│   ├── api/
│   │   ├── internal/      # Internal API endpoints
│   │   ├── v1/            # Public API endpoints
│   │   └── admin/         # Admin API endpoints
│   ├── core/
│   │   ├── config.py      # Конфігурація
│   │   ├── security.py    # Аутентифікація
│   │   └── cache.py       # Redis кешування
│   ├── db/
│   │   ├── models.py      # SQLAlchemy моделі
│   │   ├── database.py    # Database connection
│   │   └── session.py     # Session management
│   ├── schemas/           # Pydantic схеми
│   ├── services/          # Бізнес-логіка
│   └── utils/             # Утиліти
├── tests/
│   ├── unit/              # Unit тести
│   ├── integration/       # Integration тести
│   └── scenarios/         # Scenario тести
├── alembic/               # Database migrations
├── .env                   # Environment variables
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

---

## 🚀 Встановлення

### Вимоги

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (опціонально)

### Крок 1: Клонування репозиторію
```bash
git clone https://github.com/your-org/credits-system.git
cd credits-system
```

### Крок 2: Віртуальне середовище
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Крок 3: Встановлення залежностей
```bash
pip install -r requirements.txt
```

### Крок 4: Налаштування PostgreSQL

**Локально:**
```bash
# Створити базу даних
psql -U postgres
CREATE DATABASE credits_system;
\q
```

**Docker:**
```bash
docker run --name postgres_credits \
  -e POSTGRES_PASSWORD=postgres123 \
  -e POSTGRES_DB=credits_system \
  -p 5432:5432 \
  -d postgres:15
```

### Крок 5: Налаштування Redis

**Docker:**
```bash
docker run --name redis_credits \
  -p 6379:6379 \
  -d redis:7-alpine
```

### Крок 6: Налаштування .env

Створіть файл `.env`:
```env
# Database
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/credits_system

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300

# Security
INTERNAL_SERVICE_TOKEN=your-secret-service-token
ADMIN_TOKEN=your-secret-admin-token

# Application
DEBUG=True
```

### Крок 7: Міграції
```bash
alembic upgrade head
```

### Крок 8: Seed дані
```bash
python -m app.db.seed
```

---

## 🎯 Швидкий старт

### Запуск сервера
```bash
python main.py
```

Сервер запуститься на `http://localhost:8000`

### Документація API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Перевірка здоров'я системи
```bash
curl http://localhost:8000/health
```

**Відповідь:**
```json
{
  "app": "Credits System API",
  "database": "connected",
  "redis": "connected",
  "endpoints": {
    "internal": "/api/internal",
    "public": "/api/v1",
    "admin": "/api/admin"
  }
}
```

---

## 🔌 API Endpoints

### Internal API (Service-to-Service)

**Аутентифікація:** `X-Service-Token` header

| Method | Endpoint | Опис |
|--------|----------|------|
| GET | `/api/internal/credits/check/{user_id}` | Перевірка балансу |
| POST | `/api/internal/credits/calculate` | Розрахунок вартості |
| POST | `/api/internal/credits/charge` | Списання кредитів |
| POST | `/api/internal/credits/add` | Додавання кредитів |
| GET | `/api/internal/credits/balance/{user_id}` | Інформація про баланс |
| POST | `/api/internal/subscription/update` | Оновлення підписки |

### Public API (Users)

**Аутентифікація:** `Authorization: Bearer {token}` header

| Method | Endpoint | Опис |
|--------|----------|------|
| GET | `/api/v1/subscription` | Моя підписка |
| GET | `/api/v1/subscription/plans` | Доступні тарифи |
| GET | `/api/v1/transactions` | Історія транзакцій |
| POST | `/api/v1/credits/purchase` | Купити кредити |

### Admin API (Administration)

**Аутентифікація:** `X-Admin-Token` header

| Method | Endpoint | Опис |
|--------|----------|------|
| GET | `/api/admin/subscription-plans` | Список планів |
| POST | `/api/admin/subscription-plans` | Створити план |
| PUT | `/api/admin/subscription-plans/{tier}` | Оновити план |
| DELETE | `/api/admin/subscription-plans/{tier}` | Видалити план |
| PATCH | `/api/admin/subscription-plans/{tier}/multiplier` | Оновити множник |
| PATCH | `/api/admin/subscription-plans/{tier}/purchase-rate` | Оновити ставку |
| PATCH | `/api/admin/settings/exchange-rate` | Оновити курс |
| GET | `/api/admin/statistics` | Статистика |

---

## 💎 Тарифні плани

| План | Ціна/міс | Базові кредити | Бонус | Всього | Множник | Ставка покупки |
|------|----------|----------------|-------|--------|---------|----------------|
| **Basic** | $9.99 | 49,900 | 0 | 49,900 | x2.0 | 100% |
| **Standard** | $19.99 | 149,900 | 20,000 | 169,900 | x1.9 | 110% |
| **Premium** | $29.99 | 249,900 | 40,000 | 289,900 | x1.8 | 115% |

### Формула списання
```
Списано кредитів = Вартість ($) × Множник × 10,000
```

### Приклади розрахунків

**Генерація за $0.54:**

| План | Розрахунок | Кредитів |
|------|------------|----------|
| Basic | $0.54 × 2.0 × 10,000 | 10,800 |
| Standard | $0.54 × 1.9 × 10,000 | 10,260 |
| Premium | $0.54 × 1.8 × 10,000 | 9,720 |

**Економія Premium vs Basic:** ~10%

---

## 📝 Приклади використання

### 1. Створення підписки (Internal API)
```bash
curl -X POST http://localhost:8000/api/internal/subscription/update \
  -H "X-Service-Token: your-service-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "subscription_tier": "premium",
    "credits_to_add": 289900,
    "operation_id": "op_abc123"
  }'
```

**Відповідь:**
```json
{
  "success": true,
  "user_id": "user_123",
  "previous_tier": null,
  "new_tier": "premium",
  "credits_added": 289900,
  "new_balance": 289900,
  "multiplier": 1.8,
  "purchase_rate": 1.15
}
```

### 2. Списання кредитів (Internal API)
```bash
curl -X POST http://localhost:8000/api/internal/credits/charge \
  -H "X-Service-Token: your-service-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "cost_usd": 0.5412,
    "operation_id": "op_gen_456",
    "description": "AI generation template",
    "metadata": {"template_type": "invoice"}
  }'
```

**Відповідь:**
```json
{
  "success": true,
  "transaction_id": "txn_xyz789",
  "user_id": "user_123",
  "cost_usd": 0.5412,
  "credits_charged": 9742,
  "balance_before": 289900,
  "balance_after": 280158,
  "operation_id": "op_gen_456"
}
```

### 3. Перегляд підписки (Public API)
```bash
curl -X GET http://localhost:8000/api/v1/subscription \
  -H "Authorization: Bearer user_123"
```

**Відповідь:**
```json
{
  "subscription": {
    "tier": "premium",
    "name": "Преміум",
    "monthly_cost": 29.99,
    "fixed_cost": 5.00,
    "credits_included": 249900,
    "bonus_credits": 40000,
    "total_credits": 289900,
    "multiplier": 1.8,
    "purchase_rate": 1.15,
    "active": true
  },
  "credits": {
    "balance": 280158,
    "total_earned": 289900,
    "total_spent": 9742
  }
}
```

### 4. Історія транзакцій (Public API)
```bash
curl -X GET "http://localhost:8000/api/v1/transactions?limit=10" \
  -H "Authorization: Bearer user_123"
```

### 5. Статистика (Admin API)
```bash
curl -X GET http://localhost:8000/api/admin/statistics \
  -H "X-Admin-Token: your-admin-token"
```

---

## 🧪 Тестування

### Unit тести
```bash
pytest tests/unit -v
```

### Integration тести
```bash
# Запустіть сервер
python main.py

# В іншому терміналі
pytest tests/integration -v
```

### Scenario тести
```bash
pytest tests/scenarios -v -s
```

### Всі тести з coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Переглянути coverage звіт
```bash
open htmlcov/index.html
```

---

## 🚢 Deployment

### Docker Compose

Створіть `docker-compose.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/credits_system
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: credits_system
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Запуск:
```bash
docker-compose up -d
```

---

## 🔧 Troubleshooting

### База даних не підключається
```bash
# Перевірити статус PostgreSQL
psql -U postgres -c "SELECT version();"

# Перевірити чи існує база
psql -U postgres -l | grep credits_system
```

### Redis не працює
```bash
# Перевірити з'єднання
redis-cli ping

# Має повернути: PONG
```

### Міграції не застосовуються
```bash
# Перевірити поточну версію
alembic current

# Переглянути історію
alembic history

# Відкотити останню міграцію
alembic downgrade -1

# Застосувати знову
alembic upgrade head
```

### Тести падають
```bash
# Очистити тестову БД
rm test.db

# Перезапустити тести
pytest tests/ -v --tb=short
```

---

## 📚 Додаткові ресурси

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Redis Documentation](https://redis.io/docs/)

---

## 📄 Ліцензія

MIT License - див. [LICENSE](LICENSE) файл

---

## 👥 Автори

- **Your Name** - [GitHub](https://github.com/yourusername)

---

## 🤝 Contribution

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📧 Контакти

- Email: support@example.com
- Issues: [GitHub Issues](https://github.com/your-org/credits-system/issues)



