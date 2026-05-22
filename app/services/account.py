from fastapi import HTTPException, status

from app.models.user import User

async def get_account_data_service(current_user: User):
    account = current_user.account

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada."
        )
    
    return {
        "id": account.id,
        "balance": account.balance,
        "user_name": current_user.name,
        "user_email": current_user.email,
        "user_cpf": current_user.cpf
    }