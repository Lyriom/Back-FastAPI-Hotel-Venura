from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class RoomType(Base):
    __tablename__ = "room_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # simple|doble|triple
    capacidad_personas: Mapped[int] = mapped_column(Integer, nullable=False)     # 1|2|3
    precio_noche: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
