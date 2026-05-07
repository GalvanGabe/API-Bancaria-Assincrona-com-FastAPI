from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class AccountResponse(BaseModel):
    id: int
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)