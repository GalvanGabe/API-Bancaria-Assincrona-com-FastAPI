from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class AccountResponse(BaseModel):
    id: int
    balance: Decimal
    user_name: str
    user_email: str
    user_cpf: str

    model_config = ConfigDict(from_attributes=True)