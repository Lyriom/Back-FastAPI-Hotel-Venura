from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserOut


class RegisterIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    apellido: str = Field(min_length=1, max_length=120)
    email: EmailStr
    cedula: str = Field(pattern=r"^\d{10}$")
    telefono: str = Field(pattern=r"^\d{10}$")
    password: str = Field(min_length=8, max_length=4096)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterOut(TokenOut):
    user: UserOut
