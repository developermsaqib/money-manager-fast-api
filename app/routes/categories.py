from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.utils.deps import get_current_user
from app.services import categories as svc

router = APIRouter()

@router.post("", response_model=CategoryOut)
async def create_category(payload: CategoryCreate, user=Depends(get_current_user)):
    cid = await svc.create_category(user.id, payload.name, payload.color)
    return CategoryOut(id=cid, name=payload.name, color=payload.color)

@router.get("", response_model=list[CategoryOut])
async def list_categories(user=Depends(get_current_user)):
    return await svc.list_categories(user.id)

@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(category_id: str, payload: CategoryUpdate, user=Depends(get_current_user)):
    ok = await svc.update_category(user.id, category_id, payload.name, payload.color)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
    # return latest
    cats = await svc.list_categories(user.id)
    updated = next((c for c in cats if c["id"] == category_id), None)
    assert updated
    return CategoryOut(**updated)

@router.delete("/{category_id}")
async def delete_category(category_id: str, user=Depends(get_current_user)):
    ok = await svc.delete_category(user.id, category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "deleted"}
