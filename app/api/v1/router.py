from fastapi import APIRouter

from app.api.v1 import auth, users, room_types, rooms, reservations, payments_paypal, reports

api_router = APIRouter()
api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(room_types.router, prefix="/room-types", tags=["RoomTypes"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["Reservations"])
api_router.include_router(payments_paypal.router, prefix="/payments/paypal", tags=["PayPal"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
