from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from app.utils.deps import get_current_user
from app.services import transactions as svc

router = APIRouter()

@router.post("", response_model=TransactionOut)
async def create_transaction(payload: TransactionCreate, user=Depends(get_current_user)):
    tx_id = await svc.create_transaction(user.id, payload.model_dump())
    tx = await svc.get_transaction(user.id, tx_id)
    return TransactionOut(**tx)

@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    category_id: Optional[str] = Query(default=None),
    min_amount: Optional[float] = Query(default=None, gt=0),
    max_amount: Optional[float] = Query(default=None, gt=0),
    type: Optional[str] = Query(default=None, pattern="^(income|expense)$"),
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
    user=Depends(get_current_user)
):
    items = await svc.list_transactions(user.id, start=start, end=end, category_id=category_id,
                                        min_amount=min_amount, max_amount=max_amount, type=type,
                                        limit=limit, skip=skip)
    return [TransactionOut(**i) for i in items]

@router.get("/{tx_id}", response_model=TransactionOut)
async def get_transaction(tx_id: str, user=Depends(get_current_user)):
    tx = await svc.get_transaction(user.id, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Not found")
    return TransactionOut(**tx)

@router.patch("/{tx_id}", response_model=TransactionOut)
async def update_transaction(tx_id: str, payload: TransactionUpdate, user=Depends(get_current_user)):
    ok = await svc.update_transaction(user.id, tx_id, {k: v for k, v in payload.model_dump().items() if v is not None})
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    tx = await svc.get_transaction(user.id, tx_id)
    return TransactionOut(**tx)

@router.delete("/{tx_id}")
async def delete_transaction(tx_id: str, user=Depends(get_current_user)):
    ok = await svc.delete_transaction(user.id, tx_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "deleted"}
