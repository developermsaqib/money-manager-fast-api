# Money Manager API (FastAPI + MongoDB)

Production-ready hobby project to track incomes, expenses, budgets, and generate reports.  
Tech: FastAPI, Motor (MongoDB), JWT, Pydantic v2, SlowAPI rate limiting, structlog, pytest.

## Features
- JWT auth: register, login, logout (token blacklist)
- Transactions: CRUD with filters (date range, category, amount, type)
- Categories: CRUD
- Budgets: monthly per category + exceeded alert
- Reports: summary (balance), monthly (income/expense), category breakdown
- Security & DX: CORS, rate limit, structured logs, validation, error handling
- Dockerized with Compose; Swagger docs at `/docs`

---

## Quick Start

### 1) Clone & Env
```bash
cp .env.example .env
# edit JWT_SECRET, etc.
