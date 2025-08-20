from pydantic import BaseModel, Field
from typing import Optional

class Message(BaseModel):
    message: str = Field(..., examples=["ok"])
