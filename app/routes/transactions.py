from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransferCreate
from app.services.transaction import deposit_service, withdraw_service, get_transaction_history, transfer_service
from app.schemas.common import MessageResponse

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/deposit", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def deposit(transaction_data: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = current_user.account

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada."
        )
    
    await deposit_service(
        account=account,
        amount=transaction_data.amount,
        db=db
    )

    return {
        "message": "Depósito realizado com sucesso!",
        "balance": account.balance
    }

@router.post("/withdraw", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def withdraw(transaction_data: TransactionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    account = current_user.account

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada."
        )
    
    await withdraw_service(
        account=account,
        amount=transaction_data.amount,
        db=db
    )

    return {
        "message": "Saque realizado com sucesso!",
        "balance": account.balance
    }

@router.post("/transfer", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def transfer(transfer_data: TransferCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    
    await transfer_service(
        transfer_data=transfer_data,
        current_user=current_user,
        db=db
    )

    return {
        "message": "Transferência realizada com sucesso!"
    }

@router.get("/history", response_model=list[TransactionResponse], status_code=status.HTTP_200_OK)
async def transaction_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    account = current_user.account

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada."
        )
    
    transactions = await get_transaction_history(
        account_id=account.id,
        db=db
    )

    return transactions