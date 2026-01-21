from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.services.reports_service import range_for_daily, range_for_week, range_for_month, build_csv
from app.storage.files import write_bytes
from app.services.pdf_generator import generate_welcome_pdf

router = APIRouter()

@router.get("/daily")
def daily(date_: date, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    start, end = range_for_daily(date_)
    data = build_csv(db, start, end)
    rel = f"reports/daily_{start.isoformat()}.csv"
    path = write_bytes(rel, data)
    return FileResponse(path, media_type="text/csv", filename=path.name)

@router.get("/weekly")
def weekly(start: date, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    s, e = range_for_week(start)
    data = build_csv(db, s, e)
    rel = f"reports/weekly_{s.isoformat()}_{e.isoformat()}.csv"
    path = write_bytes(rel, data)
    return FileResponse(path, media_type="text/csv", filename=path.name)

@router.get("/monthly")
def monthly(year: int, month: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    s, e = range_for_month(year, month)
    data = build_csv(db, s, e)
    rel = f"reports/monthly_{year}_{month:02d}.csv"
    path = write_bytes(rel, data)
    return FileResponse(path, media_type="text/csv", filename=path.name)

@router.get("/welcome")
def welcome_pdf(_admin: User = Depends(require_admin)):
    # PDF estático de bienvenida + reglas
    rel = "reports/welcome/bienvenida_hotel_ventura.pdf"
    out_path = Path(settings.STORAGE_DIR) / rel
    generate_welcome_pdf(out_path, hotel_name="Hotel Ventura")
    return FileResponse(str(out_path), media_type="application/pdf", filename=out_path.name)
