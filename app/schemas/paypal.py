from datetime import date
from pydantic import BaseModel

class PayPalCreateOrderIn(BaseModel):
    room_id: int
    fecha_inicio: date
    fecha_fin: date

class PayPalCreateOrderOut(BaseModel):
    reservation_id: int
    paypal_order_id: str
    approve_url: str | None = None

class PayPalCaptureIn(BaseModel):
    reservation_id: int

class PayPalCaptureOut(BaseModel):
    reservation_id: int
    status: str
