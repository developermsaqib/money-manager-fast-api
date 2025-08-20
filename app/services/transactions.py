from typing import Optional, Literal
from datetime import date, datetime
from bson import ObjectId
from app.db.mongo import db

def oid(s: str) -> ObjectId:
    return ObjectId(s)

async def create_transaction(user_id: str, payload: dict) -> str:
    d = db()
    doc = {**payload, "user_id": user_id}
    res = await d.transactions.insert_one(doc)
    return str(res.inserted_id)

async def get_transaction(user_id: str, tx_id: str) -> Optional[dict]:
    d = db()
    tx = await d.transactions.find_one({"_id": oid(tx_id), "user_id": user_id})
    if not tx:
        return None
    tx["id"] = str(tx["_id"]); del tx["_id"]; del tx["user_id"]
    return tx

async def list_transactions(user_id: str, *,
                            start: Optional[date]=None, end: Optional[date]=None,
                            category_id: Optional[str]=None,
                            min_amount: Optional[float]=None, max_amount: Optional[float]=None,
                            type: Optional[str]=None,
                            limit: int=50, skip: int=0):
    d = db()
    q: dict = {"user_id": user_id}
    if start: q["date"] = {**q.get("date", {}), "$gte": start}
    if end: q["date"] = {**q.get("date", {}), "$lte": end}
    if category_id: q["category_id"] = category_id
    if min_amount is not None: q["amount"] = {**q.get("amount", {}), "$gte": min_amount}
    if max_amount is not None: q["amount"] = {**q.get("amount", {}), "$lte": max_amount}
    if type: q["type"] = type

    cur = d.transactions.find(q).sort("date", -1).skip(skip).limit(min(limit, 200))
    items = []
    async for t in cur:
        t["id"] = str(t["_id"]); del t["_id"]; del t["user_id"]
        items.append(t)
    return items

async def update_transaction(user_id: str, tx_id: str, payload: dict) -> bool:
    d = db()
    res = await d.transactions.update_one({"_id": oid(tx_id), "user_id": user_id}, {"$set": payload})
    return res.modified_count > 0

async def delete_transaction(user_id: str, tx_id: str) -> bool:
    d = db()
    res = await d.transactions.delete_one({"_id": oid(tx_id), "user_id": user_id})
    return res.deleted_count > 0
