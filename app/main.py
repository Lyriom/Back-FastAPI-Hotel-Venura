from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router  # <-- asegúrate de que esta ruta exista

app = FastAPI()

origins = [
    # 1. Desarrollo Local
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",

    # 2. Producción
    "https://hotelventura.com.ec",
    "https://www.hotelventura.com.ec",
    "https://auth.hotelventura.com.ec",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # <-- importante para Authorization, Content-Type, etc.
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
