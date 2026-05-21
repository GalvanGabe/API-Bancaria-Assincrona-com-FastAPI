from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.dependencies import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransferSchema

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

@router.post("/withdraw")
async def withdraw(transaction_data: TransactionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    account = current_user.account

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada."
        )
    
    if account.balance < transaction_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente."
        )
    
    account.balance -= transaction_data.amount
    
    transaction = Transaction(
        amount = transaction_data.amount,
        type = "withdraw",
        account_id = account.id
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(account)

    return {
        "message": "Saque realizado com sucesso!",
        "new_balance": account.balance
    }

@router.post("/transfer")
async def transfer(transfer_data: TransferSchema, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sender_account = current_user.account

    if not sender_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta do usuário não encontrada."
        )
    
    if sender_account.balance < transfer_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente."
        )
    
    query = select(User).options(selectinload(User.account)).where(User.cpf == transfer_data.destination_cpf)
    result = await db.execute(query)
    destination_user = result.scalar_one_or_none()

    if not destination_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário de destino não encontrado."
        )

    destination_account = destination_user.account

    if not destination_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta de destino não encontrada."
        )
    
    if sender_account.id == destination_account.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode transferir para a própria conta."
        )
    
    sender_account.balance -= transfer_data.amount
    destination_account.balance += transfer_data.amount

    withdraw_transaction = Transaction(
        amount = transfer_data.amount,
        type = "transfer_sent",
        account_id = sender_account.id
    )

    deposit_transaction = Transaction(
        amount = transfer_data.amount,
        type = "transfer_received",
        account_id = destination_account.id
    )

    db.add(withdraw_transaction)
    db.add(deposit_transaction)
    await db.commit()

    return {
        "message": "Transferência realizada com sucesso!"
    }