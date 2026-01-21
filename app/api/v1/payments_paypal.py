from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.reservation import Reservation
from app.schemas.paypal import PayPalCreateOrderIn, PayPalCreateOrderOut, PayPalCaptureIn, PayPalCaptureOut
from app.services.reservations_service import create_pending_reservation
from app.services import paypal_service
from app.storage.files import write_text

router = APIRouter()

@router.post("/create-order", response_model=PayPalCreateOrderOut, status_code=201)
def create_order(payload: PayPalCreateOrderIn, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    # 1) crea reserva pending
    try:
        res = create_pending_reservation(
            db,
            user_id=current.id,
            room_id=payload.room_id,
            start=payload.fecha_inicio,
            end=payload.fecha_fin,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2) PayPal order (monto)
    amount = f"{float(res.costo_total):.2f}"
    try:
        order = paypal_service.create_order(amount=amount, currency="USD", reference_id=str(res.id))
    except Exception as e:
        # si falla PayPal, cancela reserva pending para no bloquear
        res.status = "cancelled"
        db.commit()
        raise HTTPException(status_code=502, detail=f"PayPal error: {e}")

    order_id = order.get("id")
    if not order_id:
        res.status = "cancelled"
        db.commit()
        raise HTTPException(status_code=502, detail="PayPal no devolvió order id")

    res.paypal_order_id = order_id
    db.commit()
    db.refresh(res)

    approve_url = paypal_service.extract_approve_url(order)
    return PayPalCreateOrderOut(reservation_id=res.id, paypal_order_id=order_id, approve_url=approve_url)

@router.post("/capture-order", response_model=PayPalCaptureOut)
def capture_order(payload: PayPalCaptureIn, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    res = db.get(Reservation, payload.reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reserva no existe")
    if res.user_id != current.id and current.role != "admin":
        raise HTTPException(status_code=403, detail="No permitido")
    if res.status != "pending":
        raise HTTPException(status_code=400, detail=f"Reserva no está pending (status={res.status})")
    if not res.paypal_order_id:
        raise HTTPException(status_code=400, detail="Reserva no tiene paypal_order_id")

    # capture
    try:
        capture = paypal_service.capture_order(res.paypal_order_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"PayPal capture error: {e}")

    capture_id = paypal_service.extract_capture_id(capture)
    # PayPal suele devolver status COMPLETED
    pp_status = capture.get("status", "")
    if pp_status not in ["COMPLETED", "APPROVED"]:
        raise HTTPException(status_code=400, detail=f"Pago no completado (paypal status={pp_status})")

    res.status = "paid"
    res.paypal_capture_id = capture_id
    db.commit()
    db.refresh(res)

    # (Opcional) generar un "reporte" simple en texto por MVP
    # Puedes cambiarlo luego a PDF; aquí mantenemos tu requisito de "path" en carpeta.
    rel = f"reservas/{res.created_at.year}/{res.created_at.month:02d}/reserva_{res.id}.txt"
    txt = f"Reserva {res.id}\nUser: {res.user_id}\nRoom: {res.room_id}\nInicio: {res.fecha_inicio}\nFin: {res.fecha_fin}\nTotal: {float(res.costo_total):.2f}\nStatus: {res.status}\n"
    write_text(rel, txt)
    res.reporte_path = rel
    db.commit()

    return PayPalCaptureOut(reservation_id=res.id, status=res.status)
