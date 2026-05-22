from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.account import Account
from app.schemas.user import UserCreate
from app.core.security import verify_password, create_access_token, get_password_hash

async def register_service(user_data: UserCreate, db: AsyncSession):
    email_query = select(User).where(User.email == user_data.email)
    email_result = await db.execute(email_query)
    existing_email = email_result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado!"
        )
    
    cpf_query = select(User).where(User.cpf == user_data.cpf)
    cpf_result = await db.execute(cpf_query)
    existing_cpf = cpf_result.scalar_one_or_none()

    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado!"
        )
    
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        name = user_data.name,
        cpf = user_data.cpf,
        email = user_data.email,
        password_hash = hashed_password
    )

    db.add(new_user)
    await db.flush()
    account = Account(user_id = new_user.id)
    db.add(account)
    await db.commit()
    await db.refresh(new_user)

    return new_user

async def login_service(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos!"
        )
    
    password_valid = verify_password(form_data.password, user.password_hash)

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos!"
        )
    
    access_token = create_access_token(
        data={
            "sub": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }