from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from calendar import monthrange
from app.schemas.budget import BudgetSet, BudgetUpdate, BudgetOut
from app.utils.deps import get_current_user
from app.services import budgets as svc
from app.db.mongo import db

router = APIRouter()

def month_bounds(month: str):
    y, m = map(int, month.split("-"))
    start = date(y, m, 1)
    last_day = monthrange(y, m)[1]
    end = date(y, m, last_day)
    return start, end

@router.post("", response_model=BudgetOut)
async def set_budget(payload: BudgetSet, user=Depends(get_current_user)):
    bid = await svc.set_budget(user.id, payload.category_id, payload.month, payload.limit)
    # compute spent
    start, end = month_bounds(payload.month)
    d = db()
    pipeline = [
        {"$match": {"user_id": user.id, "type": "expense", "category_id": payload.category_id, "date": {"$gte": start, "$lte": end}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    total = 0.0
    async for row in d.transactions.aggregate(pipeline):
        total = row["total"]
    exceeded = total > payload.limit
    return BudgetOut(id=bid, category_id=payload.category_id, month=payload.month, limit=payload.limit, spent=total, exceeded=exceeded)

@router.get("", response_model=list[BudgetOut])
async def list_budgets(user=Depends(get_current_user)):
    items = await svc.list_budgets(user.id)
    out = []
    d = db()
    for b in items:
        start, end = month_bounds(b["month"])
        pipeline = [
            {"$match": {"user_id": user.id, "type": "expense", "category_id": b["category_id"], "date": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        spent = 0.0
        async for row in d.transactions.aggregate(pipeline):
            spent = row["total"]
        out.append(BudgetOut(id=b["id"], category_id=b["category_id"], month=b["month"], limit=b["limit"], spent=spent, exceeded=spent > b["limit"]))
    return out

@router.get("/{category_id}", response_model=BudgetOut)
async def get_budget(category_id: str, month: str = Query(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$"), user=Depends(get_current_user)):
    d = db()
    b = await d.budgets.find_one({"user_id": user.id, "category_id": category_id, "month": month})
    if not b:
        raise HTTPException(status_code=404, detail="Not found")
    start, end = month_bounds(month)
    pipeline = [
        {"$match": {"user_id": user.id, "type": "expense", "category_id": category_id, "date": {"$gte": start, "$lte": end}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    spent = 0.0
    async for row in d.transactions.aggregate(pipeline):
        spent = row["total"]
    return BudgetOut(id=str(b["_id"]), category_id=category_id, month=month, limit=b["limit"], spent=spent, exceeded=spent > b["limit"])

@router.delete("/{budget_id}")
async def delete_budget(budget_id: str, user=Depends(get_current_user)):
    ok = await svc.delete_budget(user.id, budget_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "deleted"}
