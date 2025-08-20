from datetime import datetime, timezone
from app.core.security import hash_password, verify_password, create_access_token
from app.db.mongo import db

async def create_user(email: str, password: str) -> str:
    d = db()
    user = {"_id": email.lower(), "email": email.lower(), "password": hash_password(password), "created_at": datetime.now(timezone.utc)}
    await d.users.insert_one(user)
    return user["_id"]

async def authenticate(email: str, password: str) -> str | None:
    d = db()
    user = await d.users.find_one({"_id": email.lower()})
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user["_id"]

async def blacklist_token(jti: str, exp_ts: int):
    d = db()
    await d.token_blacklist.insert_one({"jti": jti, "exp_ts": exp_ts})
