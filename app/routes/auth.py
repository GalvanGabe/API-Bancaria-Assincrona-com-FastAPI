from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserCreate, UserResponse
from app.models.account import Account
from app.core.security import get_password_hash

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
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

    account = Account(
        user_id = new_user.id
    )

    db.add(account)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email==form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos."
        )
    
    password_valid = verify_password(
        form_data.password,
        user.password_hash
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos."
        )
    
    access_token = create_access_token(
        data = {
            "sub": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }