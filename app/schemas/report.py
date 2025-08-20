from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class DateRange(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None

class SummaryOut(BaseModel):
    balance: float
    total_income: float
    total_expense: float

class MonthlyItem(BaseModel):
    month: str
    income: float
    expense: float

class MonthlyOut(BaseModel):
    items: List[MonthlyItem]

class CategoryBreakdownItem(BaseModel):
    category_id: str | None
    category_name: str | None
    expense: float
    income: float

class CategoryBreakdownOut(BaseModel):
    items: List[CategoryBreakdownItem]
