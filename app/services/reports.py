from datetime import date
from typing import Optional
from app.db.mongo import db

async def summary(user_id: str, start: Optional[date], end: Optional[date]) -> dict:
    d = db()
    q = {"user_id": user_id}
    if start: q["date"] = {**q.get("date", {}), "$gte": start}
    if end: q["date"] = {**q.get("date", {}), "$lte": end}

    pipeline = [
        {"$match": q},
        {"$group": {
            "_id": "$type",
            "total": {"$sum": "$amount"}
        }}
    ]
    totals = {"income": 0.0, "expense": 0.0}
    async for row in d.transactions.aggregate(pipeline):
        totals[row["_id"]] = row["total"]
    balance = totals["income"] - totals["expense"]
    return {"balance": balance, "total_income": totals["income"], "total_expense": totals["expense"]}

async def monthly(user_id: str, start: Optional[date], end: Optional[date]):
    d = db()
    q = {"user_id": user_id}
    if start: q["date"] = {**q.get("date", {}), "$gte": start}
    if end: q["date"] = {**q.get("date", {}), "$lte": end}
    pipeline = [
        {"$match": q},
        {"$project": {
            "type": 1,
            "amount": 1,
            "ym": {"$dateToString": {"format": "%Y-%m", "date": {"$toDate": "$date"}}}
        }},
        {"$group": {
            "_id": {"month": "$ym", "type": "$type"},
            "total": {"$sum": "$amount"}
        }},
        {"$group": {
            "_id": "$_id.month",
            "bytype": {"$push": {"type": "$_id.type", "total": "$total"}}
        }},
        {"$sort": {"_id": 1}},
    ]
    items = []
    async for row in d.transactions.aggregate(pipeline):
        income = sum(x["total"] for x in row["bytype"] if x["type"] == "income")
        expense = sum(x["total"] for x in row["bytype"] if x["type"] == "expense")
        items.append({"month": row["_id"], "income": income, "expense": expense})
    return {"items": items}

async def category_breakdown(user_id: str, start: Optional[date], end: Optional[date], categories_map: dict[str, str]):
    d = db()
    q = {"user_id": user_id}
    if start: q["date"] = {**q.get("date", {}), "$gte": start}
    if end: q["date"] = {**q.get("date", {}), "$lte": end}
    pipeline = [
        {"$match": q},
        {"$group": {"_id": {"category_id": "$category_id", "type": "$type"}, "total": {"$sum": "$amount"}}},
        {"$group": {"_id": "$_id.category_id", "bytype": {"$push": {"type": "$_id.type", "total": "$total"}}}},
    ]
    items = []
    async for row in d.transactions.aggregate(pipeline):
        cid = row["_id"]
        income = sum(x["total"] for x in row["bytype"] if x["type"] == "income")
        expense = sum(x["total"] for x in row["bytype"] if x["type"] == "expense")
        items.append({"category_id": cid, "category_name": categories_map.get(cid) if cid else None, "income": income, "expense": expense})
    return {"items": items}
