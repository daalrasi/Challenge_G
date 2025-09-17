from typing import List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# --- Catálogos (se mantienen por si los usas en otros endpoints) ---
class DepartmentIn(BaseModel):
    id: int
    department: str

class JobIn(BaseModel):
    id: int
    job: str


class HiredEmployeeIn(BaseModel):
    id: int
    name: str
    datetime: datetime
    department_id: int
    job_id: int

class BatchEmployeesIn(BaseModel):
    items: List[HiredEmployeeIn] = Field(..., description="1..1000 hired employees")