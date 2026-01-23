from pathlib import Path
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.reservation import Reservation
from app.models.room import Room
from app.models.room_type import RoomType
from app.schemas.reservation import (
    ReservationCreateIn,
    ReservationAdminCreateIn,
    ReservationUpdateIn,
    ReservationOut,
)
from app.services.reservations_service import create_pending_reservation, update_reservation_admin
from app.services.pdf_generator import generate_reservation_pdf

router = APIRouter()


# ✅ NUEVO: reservas bloqueantes para mapa (sin datos privados)
@router.get("/blocked")
def blocked_reservations(
    start: str | None = Query(default=None, description="YYYY-MM-DD"),
    end: str | None = Query(default=None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _current: User = Depends(get_current_user),  # cliente o admin logueado
):
    """
    Devuelve SOLO lo necesario para disponibilidad del hotel:
      - room_id
      - fecha_inicio
      - fecha_fin
      - status
    Solo considera reservas: pending, paid
    """
    stmt = (
        select(Reservation.room_id, Reservation.fecha_inicio, Reservation.fecha_fin, Reservation.status)
        .where(Reservation.status.in_(["pending", "paid"]))
    )

    rows = db.execute(stmt).all()

    # si no mandan fechas, devolvemos todo lo bloqueante
    if not start or not end:
        return [
            {
                "room_id": r.room_id,
                "fecha_inicio": str(r.fecha_inicio),
                "fecha_fin": str(r.fecha_fin),
                "status": r.status,
            }
            for r in rows
        ]

    # filtrado por overlap [start, end)
    try:
        s = date.fromisoformat(start)
        e = date.fromisoformat(end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Fechas inválidas. Usa YYYY-MM-DD")

    def overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
        return a_start < b_end and a_end > b_start

    out = []
    for r in rows:
        if overlaps(r.fecha_inicio, r.fecha_fin, s, e):
            out.append(
                {
                    "room_id": r.room_id,
                    "fecha_inicio": str(r.fecha_inicio),
                    "fecha_fin": str(r.fecha_fin),
                    "status": r.status,
                }
            )
    return out


@router.post("", response_model=ReservationOut, status_code=201)
def create_reservation(
    payload: ReservationCreateIn,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    try:
        res = create_pending_reservation(
            db,
            user_id=current.id,
            room_id=payload.room_id,
            start=payload.fecha_inicio,
            end=payload.fecha_fin,
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin", response_model=ReservationOut, status_code=201)
def admin_create_reservation(
    payload: ReservationAdminCreateIn,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=400, detail="Usuario no existe")
    try:
        res = create_pending_reservation(
            db,
            user_id=payload.user_id,
            room_id=payload.room_id,
            start=payload.fecha_inicio,
            end=payload.fecha_fin,
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=list[ReservationOut])
def my_reservations(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    stmt = select(Reservation).where(Reservation.user_id == current.id).order_by(Reservation.id.desc())
    return db.execute(stmt).scalars().all()


@router.get("", response_model=list[ReservationOut])
def list_all(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    stmt = select(Reservation).order_by(Reservation.id.desc())
    return db.execute(stmt).scalars().all()


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if current.role != "admin" and r.user_id != current.id:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    return r


@router.put("/{reservation_id}", response_model=ReservationOut)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdateIn,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if payload.user_id is not None and not db.get(User, payload.user_id):
        raise HTTPException(status_code=400, detail="Usuario no existe")
    if payload.room_id is not None and not db.get(Room, payload.room_id):
        raise HTTPException(status_code=400, detail="Habitación no existe")

    try:
        return update_reservation_admin(
            db,
            r,
            user_id=payload.user_id,
            room_id=payload.room_id,
            start=payload.fecha_inicio,
            end=payload.fecha_fin,
            status=payload.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{reservation_id}", status_code=204)
def delete_reservation(reservation_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db.delete(r)
    db.commit()
    return None


@router.get("/{reservation_id}/report")
def reservation_report(reservation_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if current.role != "admin" and r.user_id != current.id:
        raise HTTPException(status_code=403, detail="No tienes permiso")

    guest = db.get(User, r.user_id)
    room = db.get(Room, r.room_id)
    rtype = db.get(RoomType, room.room_type_id) if room else None

    rel = f"reservations/reserva_{r.id}.pdf"
    out_path = Path(settings.STORAGE_DIR) / rel

    generate_reservation_pdf(
        out_path,
        hotel_name="Hotel Ventura",
        reservation_id=r.id,
        guest_fullname=f"{guest.nombre} {guest.apellido}" if guest else "N/A",
        guest_email=guest.email if guest else "N/A",
        room_numero=room.numero if room else "N/A",
        room_tipo=rtype.tipo if rtype else "N/A",
        fecha_inicio=str(r.fecha_inicio),
        fecha_fin=str(r.fecha_fin),
        costo_total=str(r.costo_total),
        status=r.status,
    )

    if r.reporte_path != rel:
        r.reporte_path = rel
        db.add(r)
        db.commit()

    return FileResponse(str(out_path), media_type="application/pdf", filename=out_path.name)
