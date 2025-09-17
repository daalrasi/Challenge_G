from typing import Iterable, Tuple
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session
from datetime import datetime
from .models import Department, Job, HiredEmployee

def bulk_upsert_departments(db: Session, rows: Iterable[Tuple[int, str]]):
    stmt = pg_insert(Department).values([{"id": rid, "department": name} for rid, name in rows])
    stmt = stmt.on_conflict_do_update(index_elements=[Department.id], set_={"department": stmt.excluded.department})
    db.execute(stmt)

def bulk_upsert_jobs(db: Session, rows: Iterable[Tuple[int, str]]):
    stmt = pg_insert(Job).values([{"id": rid, "job": name} for rid, name in rows])
    stmt = stmt.on_conflict_do_update(index_elements=[Job.id], set_={"job": stmt.excluded.job})
    db.execute(stmt)

def bulk_upsert_hired_employees(db: Session, rows: Iterable[Tuple[int, str, datetime, int, int]]):
    stmt = pg_insert(HiredEmployee).values([{
        "id": rid, "name": name, "datetime": dt, "department_id": dep, "job_id": job
    } for rid, name, dt, dep, job in rows])
    stmt = stmt.on_conflict_do_update(
        index_elements=[HiredEmployee.id],
        set_={
            "name": stmt.excluded.name,
            "datetime": stmt.excluded.datetime,
            "department_id": stmt.excluded.department_id,
            "job_id": stmt.excluded.job_id,
        }
    )
    db.execute(stmt)

def metric_quarter_hires(db: Session, year: int):
    sql = text("""
       SELECT d.department, j.job,
               COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM he.datetime) = 1) AS q1,
               COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM he.datetime) = 2) AS q2,
               COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM he.datetime) = 3) AS q3,
               COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM he.datetime) = 4) AS q4
        FROM hired_employees he
        JOIN departments d ON d.id = he.department_id
        JOIN jobs j ON j.id = he.job_id
        WHERE EXTRACT(YEAR FROM he.datetime) = :year
        GROUP BY d.department, j.job
        ORDER BY d.department ASC, j.job ASC
    """ )
    return [dict(r) for r in db.execute(sql, {"year": year}).mappings().all()]

def metric_top_departments(db: Session, year: int):
    sql = text("""
       WITH per_dept AS (
  SELECT d.id, d.department,
         COALESCE(COUNT(he.id), 0) AS hired
  FROM departments d
  LEFT JOIN hired_employees he
         ON he.department_id = d.id
        AND EXTRACT(YEAR FROM he.datetime) = :year
  GROUP BY d.id, d.department
)
SELECT id, department, hired
FROM per_dept
WHERE hired > (SELECT AVG(hired) FROM per_dept)
ORDER BY hired DESC;
        
    """ )
    return [dict(r) for r in db.execute(sql, {"year": year}).mappings().all()]
