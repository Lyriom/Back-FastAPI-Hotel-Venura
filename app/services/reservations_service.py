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


def has_overlap_excluding(db: Session, *, reservation_id: int, room_id: int, start: date, end: date) -> bool:
    """Igual que has_overlap, pero excluye la reserva actual (para updates)."""
    stmt = (
        select(Reservation.id)
        .where(
            Reservation.id != reservation_id,
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


def update_reservation_admin(
    db: Session,
    reservation: Reservation,
    *,
    user_id: int | None = None,
    room_id: int | None = None,
    start: date | None = None,
    end: date | None = None,
    status: str | None = None,
) -> Reservation:
    """Actualización de reserva (solo admin).

    Recalcula costo_total si cambia el rango o la habitación.
    """
    new_user_id = reservation.user_id if user_id is None else user_id
    new_room_id = reservation.room_id if room_id is None else room_id
    new_start = reservation.fecha_inicio if start is None else start
    new_end = reservation.fecha_fin if end is None else end
    new_status = reservation.status if status is None else status

    # Validaciones solo si afecta fechas/habitación
    if start is not None or end is not None or room_id is not None:
        assert_valid_dates(new_start, new_end)

        # Si queda en un estado que bloquea fechas, validamos solapes
        if new_status in ["pending", "paid"]:
            if has_overlap_excluding(db, reservation_id=reservation.id, room_id=new_room_id, start=new_start, end=new_end):
                raise ValueError("La habitación ya está reservada en ese rango")

        reservation.costo_total = calculate_total(db, new_room_id, new_start, new_end)

    reservation.user_id = new_user_id
    reservation.room_id = new_room_id
    reservation.fecha_inicio = new_start
    reservation.fecha_fin = new_end
    reservation.status = new_status

    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation
