from pydantic import BaseModel, Field

class RoomTypeOut(BaseModel):
    id: int
    tipo: str
    capacidad_personas: int
    precio_noche: float

    class Config:
        from_attributes = True

class RoomTypeIn(BaseModel):
    tipo: str = Field(pattern=r"^(simple|doble|triple)$")
    capacidad_personas: int = Field(ge=1, le=3)
    precio_noche: float = Field(gt=0)
