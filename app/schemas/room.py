from pydantic import BaseModel, Field

class RoomOut(BaseModel):
    id: int
    numero: str
    piso: int
    estado: str
    room_type_id: int

    class Config:
        from_attributes = True

class RoomIn(BaseModel):
    numero: str = Field(min_length=1, max_length=20)
    piso: int = Field(ge=0, le=200)
    estado: str = Field(default="disponible", pattern=r"^(disponible|mantenimiento|ocupada)$")
    room_type_id: int
