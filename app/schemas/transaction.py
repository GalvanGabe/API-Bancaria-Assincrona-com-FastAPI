from decimal import Decimal
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator

class TransactionCreate(BaseModel):
    amount: Decimal
    type: Literal["deposit", "withdraw"]

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal):
        if value <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        
        return value
    
class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)