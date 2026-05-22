from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from decimal import Decimal
from fastapi import HTTPException, status

from app.models.account import Account
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import TransferCreate

async def deposit_service(account: Account, amount: Decimal, db: AsyncSession):
    account.balance += amount

    transaction = Transaction(
        amount = amount,
        type = "deposit",
        account_id = account.id
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(account)

    return transaction

async def withdraw_service(account: Account, amount: Decimal, db: AsyncSession):

    if account.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente."
        )
    
    account.balance -= amount

    transaction = Transaction(
        amount = amount,
        type = "withdraw",
        account_id = account.id
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(account)

    return transaction

async def get_transaction_history(account_id: int, db: AsyncSession):
    query = select(Transaction).where(Transaction.account_id == account_id).order_by(desc(Transaction.created_at))
    result = await db.execute(query)

    return result.scalars().all()

async def transfer_service(transfer_data: TransferCreate, current_user: User, db: AsyncSession):
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

    return