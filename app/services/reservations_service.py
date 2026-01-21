from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.models.reservation import Reservation
from app.models.room import Room
from app.models.room_type import RoomType

def nights_between(start: date, end: date) -> int:
    return (end - start).days

def assert_valid_dates(start: date, end: date) -> None:
    today = date.today()
    if start < today:
        raise ValueError("fecha_inicio no puede ser una fecha pasada")
    if end <= start:
        raise ValueError("fecha_fin debe ser mayor a fecha_inicio")

def has_overlap(db: Session, room_id: int, start: date, end: date) -> bool:
    # Solape si existe reserva pending/paid donde:
    # existing_start < new_end AND existing_end > new_start
    stmt = (
        select(Reservation.id)
        .where(
            Reservation.room_id == room_id,
            Reservation.status.in_(["pending", "paid"]),
            Reservation.fecha_inicio < end,
            Reservation.fecha_fin > start,
        )
        .limit(1)
    )
    return db.execute(stmt).first() is not None

def calculate_total(db: Session, room_id: int, start: date, end: date) -> float:
    room = db.get(Room, room_id)
    if not room:
        raise ValueError("Habitación no existe")
    rt = db.get(RoomType, room.room_type_id)
    if not rt:
        raise ValueError("Tipo de habitación no existe")

    nights = nights_between(start, end)
    if nights <= 0:
        raise ValueError("Rango inválido")
    return float(rt.precio_noche) * nights

def create_pending_reservation(db: Session, *, user_id: int, room_id: int, start: date, end: date) -> Reservation:
    assert_valid_dates(start, end)
    if has_overlap(db, room_id, start, end):
        raise ValueError("La habitación ya está reservada en ese rango")
    total = calculate_total(db, room_id, start, end)

    res = Reservation(
        user_id=user_id,
        room_id=room_id,
        fecha_inicio=start,
        fecha_fin=end,
        costo_total=total,
        status="pending",
    )
    db.add(res)
    db.commit()
    db.refresh(res)
    return res
