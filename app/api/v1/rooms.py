from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import require_admin
from app.models.room import Room
from app.models.room_type import RoomType
from app.models.user import User
from app.schemas.room import RoomOut, RoomIn

router = APIRouter()

@router.get("", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.execute(select(Room).order_by(Room.id.asc())).scalars().all()

@router.post("", response_model=RoomOut, status_code=201)
def create_room(payload: RoomIn, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    if db.execute(select(Room.id).where(Room.numero == payload.numero)).first():
        raise HTTPException(status_code=400, detail="Número de habitación ya existe")
    if not db.get(RoomType, payload.room_type_id):
        raise HTTPException(status_code=400, detail="Tipo de habitación no existe")
    r = Room(
        numero=payload.numero,
        piso=payload.piso,
        estado=payload.estado,
        room_type_id=payload.room_type_id,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.put("/{room_id}", response_model=RoomOut)
def update_room(room_id: int, payload: RoomIn, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    r = db.get(Room, room_id)
    if not r:
        raise HTTPException(status_code=404, detail="Habitación no existe")

    if payload.numero != r.numero:
        if db.execute(select(Room.id).where(Room.numero == payload.numero)).first():
            raise HTTPException(status_code=400, detail="Número de habitación ya existe")
        r.numero = payload.numero

    if not db.get(RoomType, payload.room_type_id):
        raise HTTPException(status_code=400, detail="Tipo de habitación no existe")

    r.piso = payload.piso
    r.estado = payload.estado
    r.room_type_id = payload.room_type_id
    db.commit()
    db.refresh(r)
    return r

@router.delete("/{room_id}", status_code=204)
def delete_room(room_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    r = db.get(Room, room_id)
    if not r:
        raise HTTPException(status_code=404, detail="Habitación no existe")
    db.delete(r)
    db.commit()
    return None
