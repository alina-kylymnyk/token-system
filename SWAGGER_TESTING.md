# Тестування API через Swagger UI

## Зміст
1. [Загальна інформація](#загальна-інформація)
2. [Запуск API](#запуск-api)
3. [Доступ до Swagger UI](#доступ-до-swagger-ui)
4. [Типи авторизації](#типи-авторизації)
5. [Налаштування токенів](#налаштування-токенів)
6. [Авторизація в Swagger UI](#авторизація-в-swagger-ui)
7. [Приклади тестування](#приклади-тестування)
8. [Troubleshooting](#troubleshooting)

---

## Загальна інформація

Swagger UI - це інтерактивна документація API, яка дозволяє:
- Переглядати всі доступні endpoints
- Тестувати API запити безпосередньо з браузера
- Переглядати структуру запитів та відповідей
- Авторизуватись для тестування захищених endpoints

**URL Swagger UI:** http://localhost:8000/docs
**URL ReDoc:** http://localhost:8000/redoc (альтернативна документація)

---

## Запуск API

### 1. Налаштування оточення

Створіть файл `.env` на основі `.env.example`:

```bash
cp .env.example .env
```

### 2. Заповніть необхідні змінні в `.env`

```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5433
DATABASE_USER=postgres
DATABASE_PASSWORD=your-db-password
DATABASE_NAME=credits_system

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security - ВАЖЛИВО!
INTERNAL_SERVICE_TOKEN=dev-service-token-12345
ADMIN_TOKEN=dev-admin-token-67890
```

### 3. Запустіть базу даних і Redis

```bash
docker-compose up -d
```

### 4. Виконайте seed даних (опціонально)

Seed скрипт можна запустити кількома способами:

**Спосіб 1 (рекомендований):**
```bash
python -m app.db.seed
```

**Спосіб 2:**
```bash
python app/db/seed.py
```

**Спосіб 3 (з будь-якої директорії):**
```bash
python3 app/db/seed.py
```

### 5. Запустіть API

```bash
python main.py
```

Або через uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Після запуску ви побачите повідомлення:
```
API Documentation:
  Swagger UI: http://localhost:8000/docs
  ReDoc: http://localhost:8000/redoc
```

---

## Доступ до Swagger UI

Відкрийте браузер і перейдіть на: **http://localhost:8000/docs**

Ви побачите інтерактивну документацію з трьома групами endpoints:

### 📁 Групи API

1. **Public API** (`/api/v1`) - Публічні endpoints для клієнтів
   - `/api/v1/subscription/*` - Управління підписками
   - `/api/v1/transactions/*` - Історія транзакцій
   - `/api/v1/credits/*` - Купівля кредитів

2. **Internal API** (`/api/internal`) - Endpoints для внутрішніх сервісів
   - `/api/internal/credits/*` - Операції з кредитами
   - `/api/internal/subscription/*` - Управління підписками

3. **Admin API** (`/api/admin`) - Адміністративні endpoints
   - `/api/admin/subscription-plans/*` - Управління тарифними планами
   - `/api/admin/settings/*` - Системні налаштування
   - `/api/admin/statistics/*` - Статистика системи

---

## Типи авторизації

В системі використовуються **три типи авторизації** залежно від типу API:

### 1. 🔐 Internal API - Service Token

**Заголовок:** `X-Service-Token`
**Призначення:** Для взаємодії між внутрішніми мікросервісами
**Endpoints:** `/api/internal/*`

**Приклад:**
```
X-Service-Token: dev-service-token-12345
```

### 2. 🔑 Admin API - Admin Token

**Заголовок:** `X-Admin-Token`
**Призначення:** Для адміністративних операцій
**Endpoints:** `/api/admin/*`

**Приклад:**
```
X-Admin-Token: dev-admin-token-67890
```

### 3. 👤 Public API - Bearer Token

**Заголовок:** `Authorization: Bearer {user_id}`
**Призначення:** Для аутентифікації користувачів
**Endpoints:** `/api/v1/*`

**Приклад:**
```
Authorization: Bearer user_123
```

> **ПРИМІТКА ДЛЯ DEMO:** В поточній демо-версії Bearer token - це просто user_id.
> В production версії тут має бути реальний JWT токен з перевіркою підпису.

---

## Налаштування токенів

### У файлі `.env`

Токени налаштовуються через змінні оточення у файлі `.env`:

```env
# Security Tokens
INTERNAL_SERVICE_TOKEN=your-secret-service-token
ADMIN_TOKEN=your-secret-admin-token
```

**ВАЖЛИВО:**
- Ці токени зчитуються при запуску API
- Після зміни токенів в `.env` потрібно **перезапустити** сервер


### Приклад налаштування для розробки

```env
# Development tokens (НЕ використовуйте в production!)
INTERNAL_SERVICE_TOKEN=dev-service-token-12345
ADMIN_TOKEN=dev-admin-token-67890
DEBUG=True
```

### Генерація безпечних токенів для production

```python
import secrets
print("Service Token:", secrets.token_urlsafe(32))
print("Admin Token:", secrets.token_urlsafe(32))
```

---

## Авторизація в Swagger UI

### Крок 1: Відкрийте Swagger UI

Перейдіть на http://localhost:8000/docs

### Крок 2: Знайдіть кнопку "Authorize"

В правому верхньому кутку ви побачите кнопку **🔓 Authorize**. Натисніть на неї.

### Крок 3: Оберіть тип авторизації

Ви побачите вікно з трьома секціями:

#### 🔐 APIKeyHeader (X-Service-Token)
Для Internal API endpoints

1. Натисніть на поле **Value**
2. Введіть ваш токен з `.env` (наприклад: `dev-service-token-12345`)
3. Натисніть **Authorize**
4. Натисніть **Close**

#### 🔑 APIKeyHeader (X-Admin-Token)
Для Admin API endpoints

1. Натисніть на поле **Value**
2. Введіть ваш токен з `.env` (наприклад: `dev-admin-token-67890`)
3. Натисніть **Authorize**
4. Натисніть **Close**

#### 👤 HTTPBearer
Для Public API endpoints

1. Натисніть на поле **Value**
2. Введіть user_id (наприклад: `user_123`)
3. **НЕ** додавайте слово "Bearer" - Swagger додасть його автоматично
4. Натисніть **Authorize**
5. Натисніть **Close**

### Крок 4: Перевірте авторизацію

Після успішної авторизації:
- Іконка замка 🔓 зміниться на 🔒
- Ви зможете викликати захищені endpoints
- Токени автоматично додаватимуться до кожного запиту

---

## Приклади тестування

### 📝 Приклад 1: Перевірка балансу користувача (Internal API)

**Endpoint:** `GET /api/internal/credits/balance/{user_id}`

**Кроки:**
1. Авторизуйтесь з X-Service-Token
2. Знайдіть endpoint `GET /api/internal/credits/balance/{user_id}`
3. Натисніть **Try it out**
4. Введіть `user_id`: `user_123`
5. Натисніть **Execute**

**Очікувана відповідь (200 OK):**
```json
{
  "user_id": "user_123",
  "balance": 50000,
  "subscription_tier": "basic",
  "exchange_rate": 10000,
  "current_multiplier": 2.0,
  "current_purchase_rate": 1.0
}
```

**Можливі помилки:**
- `403 Forbidden` - неправильний service token
- `404 Not Found` - користувач не знайдений

---

### 📝 Приклад 2: Створення тарифного плану (Admin API)

**Endpoint:** `POST /api/admin/subscription-plans/`

**Кроки:**
1. Авторизуйтесь з X-Admin-Token
2. Знайдіть endpoint `POST /api/admin/subscription-plans/`
3. Натисніть **Try it out**
4. Заповніть Request body:

```json
{
  "tier": "vip",
  "name": "VIP Plan",
  "monthly_cost": 49.99,
  "fixed_cost": 5.0,
  "credits_included": 500000,
  "bonus_credits": 100000,
  "multiplier": 1.5,
  "purchase_rate": 1.2,
  "active": true
}
```

5. Натисніть **Execute**

**Очікувана відповідь (201 Created):**
```json
{
  "tier": "vip",
  "name": "VIP Plan",
  "monthly_cost": 49.99,
  "credits_included": 500000,
  "bonus_credits": 100000,
  "multiplier": 1.5,
  "purchase_rate": 1.2,
  "active": true
}
```

---

### 📝 Приклад 3: Купівля кредитів (Public API)

**Endpoint:** `POST /api/v1/credits/purchase`

**Кроки:**
1. Авторизуйтесь з Bearer token (наприклад: `user_123`)
2. Знайдіть endpoint `POST /api/v1/credits/purchase`
3. Натисніть **Try it out**
4. Заповніть Request body:

```json
{
  "amount_usd": 10.0,
  "payment_method_id": "pm_test_123456"
}
```

5. Натисніть **Execute**

**Очікувана відповідь (200 OK):**
```json
{
  "success": true,
  "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
  "amount_usd": 10.0,
  "credits_added": 110000,
  "new_balance": 160000
}
```

---

### 📝 Приклад 4: Списання кредитів (Internal API)

**Endpoint:** `POST /api/internal/credits/charge`

**Кроки:**
1. Авторизуйтесь з X-Service-Token
2. Знайдіть endpoint `POST /api/internal/credits/charge`
3. Натисніть **Try it out**
4. Заповніть Request body:

```json
{
  "user_id": "user_123",
  "cost_usd": 0.5,
  "operation_id": "op_test_12345",
  "description": "API call - GPT-4",
  "metadata": {
    "model": "gpt-4",
    "tokens": 1000
  }
}
```

5. Натисніть **Execute**

**Очікувана відповідь (200 OK):**
```json
{
  "success": true,
  "transaction_id": "123e4567-e89b-12d3-a456-426614174001",
  "credits_charged": 10000,
  "balance_before": 160000,
  "balance_after": 150000,
  "operation_id": "op_test_12345"
}
```

**Можлива помилка (недостатньо кредитів):**
```json
{
  "error": "insufficient_credits",
  "required": 10000,
  "available": 5000,
  "shortfall": 5000,
  "user_id": "user_123"
}
```
**HTTP Status:** 402 Payment Required

---

### 📝 Приклад 5: Отримання статистики системи (Admin API)

**Endpoint:** `GET /api/admin/statistics/users`

**Кроки:**
1. Авторизуйтесь з X-Admin-Token
2. Знайдіть endpoint `GET /api/admin/statistics/users`
3. Натисніть **Try it out**
4. Натисніть **Execute**

**Очікувана відповідь (200 OK):**
```json
{
  "total_users": 150,
  "users_by_tier": {
    "basic": 80,
    "standard": 50,
    "premium": 20
  },
  "active_subscriptions": 145,
  "total_credits_balance": 15000000
}
```

---

## Troubleshooting

### Проблема: 403 Forbidden

**Причина:** Неправильний або відсутній токен авторизації

**Рішення:**
1. Перевірте, що токен в `.env` співпадає з токеном в Swagger
2. Перезапустіть сервер після зміни `.env`
3. Перевірте, що ви обрали правильний тип авторизації для endpoint'а
4. Натисніть кнопку **Logout** в Swagger і авторизуйтесь знову

### Проблема: 404 Not Found

**Причина:** Користувач або ресурс не існує в базі даних

**Рішення:**
1. Запустіть seed скрипт: `python app/db/seed.py`
2. Створіть користувача через Internal API
3. Перевірте правильність user_id

### Проблема: 422 Validation Error

**Причина:** Неправильний формат даних в Request body

**Рішення:**
1. Перевірте структуру JSON в Request body
2. Переконайтесь, що всі обов'язкові поля заповнені
3. Перевірте типи даних (числа, рядки, булеві значення)
4. Подивіться на схему в розділі "Schemas" внизу Swagger UI

### Проблема: 500 Internal Server Error

**Причина:** Помилка на сервері (база даних, Redis, код)

**Рішення:**
1. Перевірте, що база даних запущена: `docker-compose ps`
2. Перевірте, що Redis запущений
3. Подивіться логи сервера в консолі
4. Перевірте підключення до БД в `.env`

### Проблема: Токени не працюють після зміни

**Причина:** Сервер не перезапущено після зміни `.env`

**Рішення:**
1. Зупиніть сервер (Ctrl+C)
2. Перезапустіть: `python main.py`
3. Заново авторизуйтесь в Swagger UI

### Проблема: Swagger UI не відкривається

**Причина:** API не запущено або порт зайнятий

**Рішення:**
1. Перевірте, що API запущено: `curl http://localhost:8000/health`
2. Перевірте, що порт 8000 вільний: `lsof -i :8000`
3. Спробуйте інший порт: `uvicorn main:app --port 8001`

### Проблема: ModuleNotFoundError: No module named 'app'

**Причина:** Python не може знайти модуль app при запуску seed.py

**Рішення:**
Використовуйте один з наступних способів запуску:

```bash
# Спосіб 1 (як модуль Python - рекомендований)
python -m app.db.seed

# Спосіб 2 (з кореневої директорії проекту)
python app/db/seed.py

# Спосіб 3 (якщо ви в директорії app/db)
python3 seed.py
```

Скрипт тепер автоматично знаходить кореневу директорію проекту та файл `.env`.

---

## Додаткова інформація

### Корисні endpoints для перевірки

**Health Check:**
```
GET http://localhost:8000/health
```

**Root:**
```
GET http://localhost:8000/
```

### Альтернативні інструменти для тестування

Окрім Swagger UI, ви можете використовувати:

1. **cURL**
```bash
curl -X GET "http://localhost:8000/api/internal/credits/balance/user_123" \
  -H "X-Service-Token: dev-service-token-12345"
```

2. **Postman**
- Імпортуйте OpenAPI spec з: http://localhost:8000/openapi.json
- Налаштуйте Headers вручну

3. **HTTPie**
```bash
http GET http://localhost:8000/api/internal/credits/balance/user_123 \
  X-Service-Token:dev-service-token-12345
```

### Структура токенів для різних середовищ

**Development:**
```env
INTERNAL_SERVICE_TOKEN=dev-service-token-12345
ADMIN_TOKEN=dev-admin-token-67890
```

**Staging:**
```env
INTERNAL_SERVICE_TOKEN=stg-$(openssl rand -hex 16)
ADMIN_TOKEN=stg-$(openssl rand -hex 16)
```

**Production:**
```env
INTERNAL_SERVICE_TOKEN=prod-$(openssl rand -hex 32)
ADMIN_TOKEN=prod-$(openssl rand -hex 32)
```

### Security Best Practices

1. **Ніколи не комітьте .env файл**
   - Додайте `.env` в `.gitignore`
   - Використовуйте `.env.example` як шаблон

2. **Використовуйте сильні токени в production**
   - Мінімум 32 символи
   - Випадкові символи (букви, цифри, спецсимволи)

3. **Обертайте токени регулярно**
   - Встановіть політику ротації токенів
   - Зберігайте старі токени в secret manager

4. **Обмежуйте доступ до .env**
   - Права доступу: `chmod 600 .env`
   - Зберігайте в безпечному місці

5. **Використовуйте HTTPS в production**
   - Налаштуйте SSL сертифікати
   - Примусово перенаправляйте з HTTP на HTTPS

---
