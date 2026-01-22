from pydantic import BaseModel, EmailStr, Field, field_validator


def _assert_bcrypt_password_len(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede exceder 72 bytes (límite de bcrypt).")
    return password


class UserOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    cedula: str
    telefono: str
    role: str

    class Config:
        from_attributes = True


class UserCreateAdminIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    apellido: str = Field(min_length=1, max_length=120)
    email: EmailStr
    cedula: str = Field(pattern=r"^\d{10}$")
    telefono: str = Field(pattern=r"^\d{10}$")
    password: str = Field(min_length=8)
    role: str = Field(pattern=r"^(admin|cliente)$")

    @field_validator("password")
    @classmethod
    def _password_len(cls, v: str) -> str:
        return _assert_bcrypt_password_len(v)


class UserUpdateIn(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    apellido: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    cedula: str | None = Field(default=None, pattern=r"^\d{10}$")
    telefono: str | None = Field(default=None, pattern=r"^\d{10}$")
    role: str | None = Field(default=None, pattern=r"^(admin|cliente)$")
    password: str | None = Field(default=None, min_length=8)

    @field_validator("password")
    @classmethod
    def _password_len(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _assert_bcrypt_password_len(v)
