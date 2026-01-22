from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import RegisterIn, RegisterOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    """Registro público (cualquier persona).

    Crea usuarios con rol fijo: cliente.
    """
    email = str(payload.email).strip().lower()

    if db.execute(select(User.id).where(User.email == email)).first():
        raise HTTPException(status_code=400, detail="Email ya existe")
    if db.execute(select(User.id).where(User.cedula == payload.cedula)).first():
        raise HTTPException(status_code=400, detail="Cédula ya existe")

    try:
        password_hash = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    u = User(
        nombre=payload.nombre,
        apellido=payload.apellido,
        email=email,
        cedula=payload.cedula,
        telefono=payload.telefono,
        password_hash=password_hash,
        role="cliente",
    )
    db.add(u)
    db.commit()
    db.refresh(u)

    token = create_access_token(sub=u.email, role=u.role, expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": token, "token_type": "bearer", "user": u}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger manda "username", nosotros lo tratamos como email
    email = form.username.strip().lower()
    password = form.password

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(sub=user.email, role=user.role, expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": token, "token_type": "bearer"}
