# app/main.py
import io, csv, json
from datetime import datetime
from typing import Literal

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .db import SessionLocal, engine, Base
from . import schemas, crud

app = FastAPI(
    title="Globant Challenge Daniel Silva",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Liveness & readiness."},
        {"name": "Ingestion", "description": "CSV & batch ingestion endpoints."},
        {"name": "Metrics", "description": "Analytical queries."},
    ],
)

# Crea tablas si no existen (demo local)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/healthz", tags=["Health"])
def healthz():
    return {"status": "ok"}

# ---------- Helpers ----------
def _looks_like_header(first_cell: str) -> bool:
    """Devuelve True si la primera celda NO es un entero (probable header)."""
    s = (first_cell or "").strip()
    return not s.isdigit()

def _parse_iso_dt(s: str) -> datetime:
    """Soporta '2021-01-01T10:00:00Z' y '2021-01-01 10:00:00'."""
    s = (s or "").strip().replace(" ", "T")
    if s.endswith("Z"):
        s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)

# ---------- Ingesta ----------
@app.post(
    "/upload_csv",
    tags=["Ingestion"],
    responses={
        200: {"description": "CSV cargado", "content": {"application/json": {"example": {"inserted_or_updated": 10, "skipped_rows": 0}}}},
        400: {"description": "Error de parseo/DB"},
        422: {"description": "Error de validación"},
    },
)
async def upload_csv(
    table: Literal["departments", "jobs", "hired_employees"] = Query(..., description="Target table"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    reader = csv.reader(io.StringIO(content.decode("utf-8")))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="Empty CSV")

    # Si detectamos header, lo saltamos
    if _looks_like_header(rows[0][0] if rows and rows[0] else ""):
        rows = rows[1:]

    try:
        if table == "departments":
            parsed, skipped = [], 0
            for r in rows:
                if not r or len(r) < 2:
                    continue
                try:
                    rid = int(r[0].strip())
                    department = r[1].strip()
                    parsed.append((rid, department))
                except Exception:
                    skipped += 1
            if not parsed and skipped > 0:
                raise HTTPException(status_code=400, detail="All rows invalid for departments")
            with db.begin():
                crud.bulk_upsert_departments(db, parsed)
            return {"inserted_or_updated": len(parsed), "skipped_rows": skipped}

        elif table == "jobs":
            parsed, skipped = [], 0
            for r in rows:
                if not r or len(r) < 2:
                    continue
                try:
                    rid = int(r[0].strip())
                    job = r[1].strip()
                    parsed.append((rid, job))
                except Exception:
                    skipped += 1
            if not parsed and skipped > 0:
                raise HTTPException(status_code=400, detail="All rows invalid for jobs")
            with db.begin():
                crud.bulk_upsert_jobs(db, parsed)
            return {"inserted_or_updated": len(parsed), "skipped_rows": skipped}

        else:  # hired_employees
            parsed, skipped = [], 0
            for r in rows:
                if not r or len(r) < 5:
                    continue
                try:
                    rid = int(r[0].strip())
                    name = r[1].strip()
                    dt = _parse_iso_dt(r[2])
                    dep = int(r[3].strip())
                    job = int(r[4].strip())
                    parsed.append((rid, name, dt, dep, job))
                except Exception:
                    skipped += 1

            if not parsed and skipped > 0:
                raise HTTPException(
                    status_code=400,
                    detail="CSV parse/insert error: all rows invalid or header-only file",
                )

            try:
                with db.begin():
                    crud.bulk_upsert_hired_employees(db, parsed)
            except SQLAlchemyError as e:
                raise HTTPException(
                    status_code=400,
                    detail={"code": "DB_ERROR", "message": "failed to upsert hired_employees", "error": str(e)},
                )
            return {"inserted_or_updated": len(parsed), "skipped_rows": skipped}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV parse/insert error: {e}")


@app.post(
    "/insert_batch",
    tags=["Ingestion"],
    responses={
        200: {"description": "Batch correct", "content": {"application/json": {"example": {"inserted_or_updated": 2}}}},
        400: {"description": "Bussines rule / DB ( >1000 items, FK)"},
        422: {"description": "Error payload"},
    },
)
async def insert_batch(payload: schemas.BatchEmployeesIn, db: Session = Depends(get_db)):
    items = payload.items
    if not (1 <= len(items) <= 1000):
        raise HTTPException(status_code=400, detail="items length must be between 1 and 1000")

    parsed = [(i.id, i.name, i.datetime, i.department_id, i.job_id) for i in items]
    try:
        with db.begin():
            crud.bulk_upsert_hired_employees(db, parsed)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": "DB_ERROR", "message": "failed to upsert hired_employees", "error": str(e)},
        )
    return {"inserted_or_updated": len(parsed)}


@app.post(
    "/insert_batch_file",
    tags=["Ingestion"],
    responses={
        200: {"description": "Batch (archivo JSON) aceptado", "content": {"application/json": {"example": {"inserted_or_updated": 10}}}},
        400: {"description": "Regla de negocio / DB"},
        422: {"description": "Error de validación del archivo"},
    },
)
async def insert_batch_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    payload = json.loads((await file.read()).decode("utf-8"))
    data = schemas.BatchEmployeesIn(**payload)  # valida por ID (department_id, job_id)
    items = data.items
    if not (1 <= len(items) <= 1000):
        raise HTTPException(status_code=400, detail="items length must be between 1 and 1000")
    parsed = [(i.id, i.name, i.datetime, i.department_id, i.job_id) for i in items]
    try:
        with db.begin():
            crud.bulk_upsert_hired_employees(db, parsed)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": "DB_ERROR", "message": "failed to upsert hired_employees", "error": str(e)},
        )
    return {"inserted_or_updated": len(parsed)}

# ---------- Métricas ----------
@app.get("/metrics/q_hires", tags=["Metrics"])
def q_hires(year: int = 2021, db: Session = Depends(get_db)):
    data = crud.metric_quarter_hires(db, year)
    return JSONResponse(content=data)

@app.get("/metrics/top_departments", tags=["Metrics"])
def top_departments(year: int = 2021, db: Session = Depends(get_db)):
    data = crud.metric_top_departments(db, year)
    return JSONResponse(content=data)
