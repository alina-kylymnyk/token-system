# Архітектура Credits System

## Загальна схема
```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│    (Web App, Mobile App, Other Microservices)               │
└────────────────┬────────────────────────────┬───────────────┘
                 │                             │
                 ▼                             ▼
┌────────────────────────────┐  ┌─────────────────────────────┐
│      Public API (v1)       │  │   Internal API              │
│  Bearer Auth               │  │   Service Token Auth        │
│  - User endpoints          │  │   - Credit operations       │
│  - Public data             │  │   - Subscription mgmt       │
└────────────┬───────────────┘  └────────────┬────────────────┘
             │                                │
             └────────────┬───────────────────┘
                          ▼
            ┌─────────────────────────────┐
            │      Services Layer         │
            ├─────────────────────────────┤
            │  • CreditService            │
            │  • SubscriptionService      │
            │  • TransactionService       │
            │  • CacheService             │
            └────────────┬────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │    Redis     │ │  External    │
│  Database    │ │    Cache     │ │  Services    │
│              │ │              │ │  (Payment)   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Database Schema
```sql
┌─────────────────────────┐
│  subscription_plans     │
├─────────────────────────┤
│ tier (PK)               │
│ name                    │
│ monthly_cost            │
│ credits_included        │
│ multiplier              │
│ purchase_rate           │
└────────────┬────────────┘
             │ 1:N
             │
┌────────────▼────────────┐
│  users                  │
├─────────────────────────┤
│ user_id (PK)            │
│ subscription_tier (FK)  │
│ created_at              │
└────────────┬────────────┘
             │ 1:1
             │
┌────────────▼────────────┐
│  credit_balances        │
├─────────────────────────┤
│ id (PK)                 │
│ user_id (FK, UNIQUE)    │
│ balance                 │
│ total_earned            │
│ total_spent             │
└────────────┬────────────┘
             │ 1:N
             │
┌────────────▼────────────┐
│  transactions           │
├─────────────────────────┤
│ id (PK)                 │
│ transaction_id (UNIQUE) │
│ user_id (FK)            │
│ operation_id (UNIQUE)   │
│ type                    │
│ credits                 │
│ balance_after           │
└─────────────────────────┘
```

## Security Layers

1. **Transport Security**: HTTPS
2. **Authentication**: Token-based (Service/Bearer/Admin)
3. **Authorization**: Role-based access
4. **Input Validation**: Pydantic schemas
5. **SQL Injection**: SQLAlchemy ORM
6. **Rate Limiting**: Per endpoint/user

## Scalability Considerations

- **Horizontal scaling**: Stateless API servers
- **Database**: Connection pooling, read replicas
- **Cache**: Redis cluster for high availability
- **Load balancer**: Distribute traffic across instances