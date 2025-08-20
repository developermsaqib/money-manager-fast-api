from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.mongo import connect_to_mongo, close_mongo_connection, ensure_indexes
from app.routes import auth, categories, transactions, budgets, reports, health
from app.utils.rate_limit import limiter

configure_logging()

app = FastAPI(
    title="Money Manager API",
    version="1.0.0",
    description="Backend API for tracking personal finances (FastAPI + MongoDB).",
    contact={"name": "Your Name", "url": "https://example.com", "email": "dev@example.com"},
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

# Startup / Shutdown
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    await ensure_indexes()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
