from datetime import date, datetime
from pydantic import BaseModel, Field

class ReservationCreateIn(BaseModel):
    room_id: int
    fecha_inicio: date
    fecha_fin: date

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
