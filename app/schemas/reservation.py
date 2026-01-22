from datetime import date, datetime
from pydantic import BaseModel, Field


class ReservationCreateIn(BaseModel):
    room_id: int
    fecha_inicio: date
    fecha_fin: date


class ReservationAdminCreateIn(ReservationCreateIn):
    user_id: int


class ReservationUpdateIn(BaseModel):
    # Solo admin
    user_id: int | None = None
    room_id: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    status: str | None = Field(default=None, pattern=r"^(pending|paid|cancelled)$")


class ReservationOut(BaseModel):
    id: int
    user_id: int
    room_id: int
    fecha_inicio: date
    fecha_fin: date
    costo_total: float
    reporte_path: str | None
    created_at: datetime
    status: str

    class Config:
        from_attributes = True
