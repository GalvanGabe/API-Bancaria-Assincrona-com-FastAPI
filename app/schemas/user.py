from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    name: str
    cpf: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    cpf: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)