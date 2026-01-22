from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserOut


def _assert_bcrypt_password_len(password: str) -> str:
    # bcrypt tiene límite de 72 bytes (no caracteres). Evitamos 500 al hashear.
    if len(password.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede exceder 72 bytes (límite de bcrypt).")
    return password


class RegisterIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    apellido: str = Field(min_length=1, max_length=120)
    email: EmailStr
    cedula: str = Field(pattern=r"^\d{10}$")
    telefono: str = Field(pattern=r"^\d{10}$")
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def _password_len(cls, v: str) -> str:
        return _assert_bcrypt_password_len(v)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterOut(TokenOut):
    user: UserOut
