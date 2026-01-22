from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

app = FastAPI()

origins = [
    "https://hotelventura.com.ec",
    "https://www.hotelventura.com.ec",
    "https://auth.hotelventura.com.ec",
    "http://localhost:5173",  
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"], 
)

app.include_router(api_router, prefix="/api/v1")
