from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Date, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False)

    fecha_inicio: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    costo_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # path relativo (ej: reservas/2026/01/reserva_15.csv o .pdf)
    reporte_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # PayPal
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending|paid|cancelled
    paypal_order_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    paypal_capture_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)

    user = relationship("User")
    room = relationship("Room")
