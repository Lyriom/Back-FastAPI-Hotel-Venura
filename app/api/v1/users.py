from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import require_admin, hash_password
from app.models.user import User
from app.schemas.user import UserOut, UserCreateAdminIn, UserUpdateIn

router = APIRouter()

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return db.execute(select(User).order_by(User.id.asc())).scalars().all()

@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreateAdminIn, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    if db.execute(select(User.id).where(User.email == str(payload.email))).first():
        raise HTTPException(status_code=400, detail="Email ya existe")
    if db.execute(select(User.id).where(User.cedula == payload.cedula)).first():
        raise HTTPException(status_code=400, detail="Cédula ya existe")

    u = User(
        nombre=payload.nombre,
        apellido=payload.apellido,
        email=str(payload.email),
        cedula=payload.cedula,
        telefono=payload.telefono,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdateIn, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no existe")

    # unique checks if changing email/cedula
    if payload.email and str(payload.email) != u.email:
        if db.execute(select(User.id).where(User.email == str(payload.email))).first():
            raise HTTPException(status_code=400, detail="Email ya existe")
        u.email = str(payload.email)

    if payload.cedula and payload.cedula != u.cedula:
        if db.execute(select(User.id).where(User.cedula == payload.cedula)).first():
            raise HTTPException(status_code=400, detail="Cédula ya existe")
        u.cedula = payload.cedula

    if payload.nombre is not None:
        u.nombre = payload.nombre
    if payload.apellido is not None:
        u.apellido = payload.apellido
    if payload.telefono is not None:
        u.telefono = payload.telefono
    if payload.role is not None:
        u.role = payload.role
    if payload.password is not None:
        u.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(u)
    return u

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no existe")
    db.delete(u)
    db.commit()
    return None
