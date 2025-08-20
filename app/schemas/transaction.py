from pydantic import BaseModel, Field, condecimal
from typing import Optional, Literal
from datetime import date

TransactionType = Literal["income", "expense"]

class TransactionBase(BaseModel):
    type: TransactionType
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    date: date
    category_id: Optional[str] = None
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    date: Optional[date] = None
    category_id: Optional[str] = None
    description: Optional[str] = None

class TransactionOut(TransactionBase):
    id: str
