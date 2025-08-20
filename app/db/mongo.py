from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

async def connect_to_mongo():
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
        _db = _client[settings.MONGO_DB_NAME]

async def close_mongo_connection():
    global _client
    if _client is not None:
        _client.close()
        _client = None

def db() -> AsyncIOMotorDatabase:
    assert _db is not None, "DB not initialized. Ensure startup hooks ran."
    return _db

async def ensure_indexes():
    d = db()
    # Users: email unique
    await d.users.create_index("email", unique=True)
    # Transactions: user_id + date + category + amount
    await d.transactions.create_index([("user_id", 1), ("date", -1)])
    await d.transactions.create_index([("user_id", 1), ("category_id", 1)])
    await d.transactions.create_index([("user_id", 1), ("amount", 1)])
    # Categories: user_id + name unique
    await d.categories.create_index([("user_id", 1), ("name", 1)], unique=True)
    # Budgets: user_id + category_id + month unique
    await d.budgets.create_index([("user_id", 1), ("category_id", 1), ("month", 1)], unique=True)
    # Token blacklist: jti with TTL on exp
    await d.token_blacklist.create_index("jti", unique=True)
    # Optional TTL index on 'exp_ts' to auto-purge expired tokens if desired:
    await d.token_blacklist.create_index("exp_ts", expireAfterSeconds=0)
