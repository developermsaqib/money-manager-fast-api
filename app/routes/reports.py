from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from app.schemas.report import SummaryOut, MonthlyOut, CategoryBreakdownOut
from app.utils.deps import get_current_user
from app.services import reports as svc_reports
from app.services.categories import get_category_map

router = APIRouter()

@router.get("/summary", response_model=SummaryOut)
async def report_summary(
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    user=Depends(get_current_user)
):
    return await svc_reports.summary(user.id, start, end)

@router.get("/monthly", response_model=MonthlyOut)
async def report_monthly(
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    user=Depends(get_current_user)
):
    return await svc_reports.monthly(user.id, start, end)

@router.get("/categories", response_model=CategoryBreakdownOut)
async def report_categories(
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    user=Depends(get_current_user)
):
    cmap = await get_category_map(user.id)
    return await svc_reports.category_breakdown(user.id, start, end, cmap)
