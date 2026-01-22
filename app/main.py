from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- 1. IMPORTAR

app = FastAPI()

# 2. DEFINIR ORÍGENES PERMITIDOS
origins = [
    "http://localhost:5173",      # Tu frontend local (Vite)
    "http://127.0.0.1:5173",      # Alternativa local
    "http://localhost:5174",      # Tu frontend local (Vite)
    "http://127.0.0.1:5174",      # Alternativa local
]

# 3. AGREGAR EL MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Lista de orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],          # Permitir todos los métodos (GET, POST, DELETE, etc.)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}
