# Hotel Ventura MVP - FastAPI + Postgres + PayPal (pending) + CSV reports

Este proyecto es un **starter MVP** con:
- FastAPI + JWT Bearer (roles: admin/cliente)
- SQLAlchemy 2.0 + Alembic (migraciones)
- 4 tablas: users, room_types, rooms, reservations (+ columnas PayPal en reservations)
- Reservas con validación de fechas y **solapes**
- PayPal Orders v2: create-order + capture-order (flujo **pending**)
- Reportes CSV: diario/semanal/mensual (solo admin)
- Guardado de archivos en disco persistente: `STORAGE_DIR` (recomendado `/data` con Railway Volume)

## Estructura
```
app/
  main.py
  core/ (config, database, security)
  models/ (SQLAlchemy)
  schemas/ (Pydantic)
  api/v1/ (routers)
  services/ (lógica)
  storage/ (helpers de archivos)
alembic/
```

## Ejecutar local
1) Copia `.env.example` a `.env` y ajusta `DATABASE_URL` (Postgres local o Railway).
2) Instala deps:
```bash
pip install -r requirements.txt
```
3) Migra:
```bash
alembic upgrade head
```
4) Corre:
```bash
uvicorn app.main:app --reload
```

## Deploy en Railway
1) Crea un proyecto y añade Postgres.
2) En variables de entorno, configura `DATABASE_URL`, `SECRET_KEY`, `STORAGE_DIR=/data`, PayPal keys.
3) Crea un **Volume** y monta en `/data` para persistencia de archivos.
4) Deploy con Dockerfile incluido.

## Admin inicial
Por MVP, puedes crear un admin de 2 maneras:
- Registrar usuario y luego cambiar `role='admin'` directamente en BD (rápido para pruebas).
- O crear un endpoint temporal solo en desarrollo (no incluido por seguridad).
