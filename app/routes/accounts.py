from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.account import AccountResponse
from app.services.account import get_account_data_service

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)

@router.get("/me", response_model=AccountResponse, status_code=status.HTTP_200_OK)
async def get_account_data(current_user: User = Depends(get_current_user)):
    account_data = await get_account_data_service(current_user)

    return account_data