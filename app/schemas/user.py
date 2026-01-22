from pydantic import BaseModel, EmailStr, Field


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
    password: str = Field(min_length=8, max_length=4096)
    role: str = Field(pattern=r"^(admin|cliente)$")


class UserUpdateIn(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    apellido: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    cedula: str | None = Field(default=None, pattern=r"^\d{10}$")
    telefono: str | None = Field(default=None, pattern=r"^\d{10}$")
    role: str | None = Field(default=None, pattern=r"^(admin|cliente)$")
    password: str | None = Field(default=None, min_length=8, max_length=4096)
