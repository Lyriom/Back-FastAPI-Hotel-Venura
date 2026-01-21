from __future__ import annotations

import csv
import io
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.reservation import Reservation
from app.models.room import Room
from app.models.room_type import RoomType

def range_for_daily(day: date) -> tuple[date, date]:
    return day, day + timedelta(days=1)

def range_for_week(start: date) -> tuple[date, date]:
    return start, start + timedelta(days=7)

def range_for_month(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end

def build_csv(db: Session, start: date, end: date) -> bytes:
    # Trae reservas paid dentro del rango
    stmt = (
        select(
            Reservation.id,
            Reservation.fecha_inicio,
            Reservation.fecha_fin,
            Reservation.costo_total,
            Room.numero,
            RoomType.tipo,
            Reservation.user_id,
        )
        .join(Room, Room.id == Reservation.room_id)
        .join(RoomType, RoomType.id == Room.room_type_id)
        .where(
            Reservation.status == "paid",
            Reservation.created_at >= start,
            Reservation.created_at < end,
        )
        .order_by(Reservation.created_at.asc())
    )
    rows = db.execute(stmt).all()

    # Totales
    total_ingresos = sum(float(r.costo_total) for r in rows) if rows else 0.0
    total_reservas = len(rows)

    by_tipo = {}
    for r in rows:
        by_tipo[r.tipo] = by_tipo.get(r.tipo, 0) + 1

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["reporte_desde", start.isoformat(), "reporte_hasta", end.isoformat()])
    w.writerow(["total_reservas", total_reservas])
    w.writerow(["total_ingresos", f"{total_ingresos:.2f}"])
    w.writerow([])
    w.writerow(["reservas_por_tipo"])
    w.writerow(["tipo", "cantidad"])
    for k, v in sorted(by_tipo.items()):
        w.writerow([k, v])
    w.writerow([])
    w.writerow(["detalle_reservas"])
    w.writerow(["reservation_id", "user_id", "room_numero", "tipo", "fecha_inicio", "fecha_fin", "costo_total"])
    for r in rows:
        w.writerow([r.id, r.user_id, r.numero, r.tipo, r.fecha_inicio.isoformat(), r.fecha_fin.isoformat(), f"{float(r.costo_total):.2f}"])

    return out.getvalue().encode("utf-8")
