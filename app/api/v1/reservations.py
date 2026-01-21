from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
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
from app.schemas.reservation import ReservationCreateIn, ReservationOut
from app.services.reservations_service import create_pending_reservation
from app.services.pdf_generator import generate_reservation_pdf

router = APIRouter()

@router.post("", response_model=ReservationOut, status_code=201)
def create_reservation(payload: ReservationCreateIn, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
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

@router.get("/me", response_model=list[ReservationOut])
def my_reservations(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    stmt = select(Reservation).where(Reservation.user_id == current.id).order_by(Reservation.id.desc())
    return db.execute(stmt).scalars().all()

@router.get("", response_model=list[ReservationOut])
def list_all(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    stmt = select(Reservation).order_by(Reservation.id.desc())
    return db.execute(stmt).scalars().all()

@router.get("/{reservation_id}/report")
def reservation_report(reservation_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    # permisos: admin ve todo, cliente solo lo suyo
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

    # guardar path en DB
    if r.reporte_path != rel:
        r.reporte_path = rel
        db.add(r)
        db.commit()

    return FileResponse(str(out_path), media_type="application/pdf", filename=out_path.name)
