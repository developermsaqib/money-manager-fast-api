from bson import ObjectId
from typing import Optional
from app.db.mongo import db

def oid(s: str) -> ObjectId:
    return ObjectId(s)

async def set_budget(user_id: str, category_id: str, month: str, limit: float) -> str:
    d = db()
    doc = {"user_id": user_id, "category_id": category_id, "month": month, "limit": limit}
    # upsert
    res = await d.budgets.update_one(
        {"user_id": user_id, "category_id": category_id, "month": month},
        {"$set": doc},
        upsert=True
    )
    if res.upserted_id:
        return str(res.upserted_id)
    # find existing
    existing = await d.budgets.find_one({"user_id": user_id, "category_id": category_id, "month": month})
    return str(existing["_id"])

async def get_budget_status(user_id: str, category_id: str, month: str) -> dict | None:
    d = db()
    b = await d.budgets.find_one({"user_id": user_id, "category_id": category_id, "month": month})
    if not b:
        return None
    # compute spent in that month (expenses only)
    start = month + "-01"
    y, m = month.split("-")
    y, m = int(y), int(m)
    if m == 12:
        end_month = f"{y+1}-01-01"
    else:
        end_month = f"{y}-{m+1:02d}-01"
    q = {"user_id": user_id, "category_id": category_id, "type": "expense", "date": {"$gte": start, "$lt": end_month}}
    # dates are stored as date objects; to compare with strings we should build date ranges instead in routes. Here we assume routes send real dates.
    # We'll compute in route using Python dates; this function expects the route to pass spent.
    return {"id": str(b["_id"]), "limit": b["limit"]}

async def list_budgets(user_id: str):
    d = db()
    cur = d.budgets.find({"user_id": user_id})
    return [ { "id": str(b["_id"]), "category_id": b["category_id"], "month": b["month"], "limit": b["limit"] } async for b in cur ]

async def delete_budget(user_id: str, budget_id: str) -> bool:
    d = db()
    res = await d.budgets.delete_one({"_id": oid(budget_id), "user_id": user_id})
    return res.deleted_count > 0
