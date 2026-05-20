from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/deposit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def deposit(transaction_data: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = current_user.account
    account.balance += transaction_data.amount

    transaction = Transaction(
        type = "deposit",
        amount = transaction_data.amount,
        account_id = account.id
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return transaction