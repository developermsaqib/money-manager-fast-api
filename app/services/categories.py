from typing import List, Optional
from app.db.mongo import db
from bson import ObjectId

def oid(s: str) -> ObjectId:
    return ObjectId(s)

async def create_category(user_id: str, name: str, color: str | None) -> str:
    d = db()
    doc = {"user_id": user_id, "name": name, "color": color}
    res = await d.categories.insert_one(doc)
    return str(res.inserted_id)

async def list_categories(user_id: str) -> list[dict]:
    d = db()
    cur = d.categories.find({"user_id": user_id})
    return [ { "id": str(c["_id"]), "name": c["name"], "color": c.get("color") } async for c in cur ]

async def update_category(user_id: str, category_id: str, name: str | None, color: str | None) -> bool:
    d = db()
    updated = await d.categories.update_one({"_id": oid(category_id), "user_id": user_id}, {"$set": {k:v for k,v in {"name": name, "color": color}.items() if v is not None}})
    return updated.modified_count > 0

async def delete_category(user_id: str, category_id: str) -> bool:
    d = db()
    # Optionally, you could also unset category_id from transactions
    deleted = await d.categories.delete_one({"_id": oid(category_id), "user_id": user_id})
    return deleted.deleted_count > 0

async def get_category_map(user_id: str) -> dict[str, str]:
    d = db()
    cur = d.categories.find({"user_id": user_id})
    return { str(c["_id"]): c["name"] async for c in cur }
