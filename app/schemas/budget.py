from pydantic import BaseModel, Field
from typing import Optional

class BudgetSet(BaseModel):
    category_id: str
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", examples=["2025-08"])
    limit: float = Field(gt=0)

class BudgetUpdate(BaseModel):
    limit: float = Field(gt=0)

class BudgetOut(BaseModel):
    id: str
    category_id: str
    month: str
    limit: float
    spent: float
    exceeded: bool
