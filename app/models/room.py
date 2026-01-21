from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    piso: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="disponible")

    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False)
    room_type = relationship("RoomType")
