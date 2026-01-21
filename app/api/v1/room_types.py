from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import require_admin
from app.models.room_type import RoomType
from app.models.user import User
from app.schemas.room_type import RoomTypeOut, RoomTypeIn

router = APIRouter()

@router.get("", response_model=list[RoomTypeOut])
def list_room_types(db: Session = Depends(get_db)):
    return db.execute(select(RoomType).order_by(RoomType.id.asc())).scalars().all()

@router.post("", response_model=RoomTypeOut, status_code=201)
def create_room_type(payload: RoomTypeIn, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    # tipo unique
    if db.execute(select(RoomType.id).where(RoomType.tipo == payload.tipo)).first():
        raise HTTPException(status_code=400, detail="Tipo ya existe")
    rt = RoomType(tipo=payload.tipo, capacidad_personas=payload.capacidad_personas, precio_noche=payload.precio_noche)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt

@router.put("/{room_type_id}", response_model=RoomTypeOut)
def update_room_type(room_type_id: int, payload: RoomTypeIn, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    rt = db.get(RoomType, room_type_id)
    if not rt:
        raise HTTPException(status_code=404, detail="Tipo no existe")

    # if tipo changes
    if payload.tipo != rt.tipo:
        if db.execute(select(RoomType.id).where(RoomType.tipo == payload.tipo)).first():
            raise HTTPException(status_code=400, detail="Tipo ya existe")
        rt.tipo = payload.tipo

    rt.capacidad_personas = payload.capacidad_personas
    rt.precio_noche = payload.precio_noche
    db.commit()
    db.refresh(rt)
    return rt

@router.delete("/{room_type_id}", status_code=204)
def delete_room_type(room_type_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    rt = db.get(RoomType, room_type_id)
    if not rt:
        raise HTTPException(status_code=404, detail="Tipo no existe")
    db.delete(rt)
    db.commit()
    return None
