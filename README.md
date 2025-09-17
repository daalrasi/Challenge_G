# Globant Challenge Daniel Silva
Deployment Challenge_G

This project implements the Globant Challenge Daniel Silva using 
**FastAPI, PostgreSQL, and Docker**.  
It used for data ingestion from CSV files, batch inserts with validation, and analytical queries for reporting.  
<img width="468" height="116" alt="image" src="https://github.com/user-attachments/assets/037ae4d8-1d62-45bc-9b17-08be9fb28ce3" />
## Tech Stack

- **FastAPI**
- **PostgreSQL**
- **Docker Compose**
- **SQLAlchemy**
- **Pydantic**
  
<img width="468" height="116" alt="image" src="https://github.com/user-attachments/assets/037ae4d8-1d62-45bc-9b17-08be9fb28ce3" />

## Running the Application

requeriments.txt: This file has content related to requirements to external packages needed to run API functionalities.

Clone the repository and start the services with Docker Compose:

bash
docker compose up --build



The following services will be available:

•	API: http://localhost:8081/docs

•	Database: PostgreSQL exposed at localhost:5432

<img width="468" height="116" alt="image" src="https://github.com/user-attachments/assets/037ae4d8-1d62-45bc-9b17-08be9fb28ce3" />

## API Endpoints

- **verify the API is running**
- **curl http://localhost:8081/healthz**

Response:
{"status":"ok"}

## CSV Upload
Upload data directly into the target tables: departments, jobs, hired_employees.

Example – Upload:

curl -F "file=@departments.csv" "http://localhost:8081/upload_csv?table=departments"

Response:
{"inserted_or_updated": 12, "skipped_rows": 0}

Tables supported:
- **departments(id, department)**
-	**jobs(id, job)**
-	**hired_employees(id, name, datetime, department_id, job_id)**
 

## POST /insert_batch

- **Batch insert (JSON)**  
  http://localhost:8081/docs#/Ingestion/insert_batch_insert_batch_post

- **batch_1000.json -- Example Especific 1000**
- **batch_1001.json -- Example more 1000**


schema json

{
  "items": [
    { "id": 50021, "name": "User A", "datetime": "2021-02-03T08:00:00", "department_id": 1, "job_id": 1 },
    { "id": 50022, "name": "User B", "datetime": "2021-02-04T09:00:00", "department_id": 2, "job_id": 2 }
  ]
}



## Query SQL

Generate the metrics quarterly hires

## Number of Employees

- **Quarterly Hires**  
  http://localhost:8081/docs#/Metrics/q_hires_metrics_q_hires_get

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

## List Of Ids

- **Top Departments**  
  http://localhost:8081/docs#/Metrics/top_departments_metrics_top_departments_get

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

## Automated Tests

Run locally:

requeriments-dev.txt: This file has content related to requirements to external packages needed to test.

bash

- **make test** 
- **make test-clean** 


## Errors

Type errors:

### 200 — Success

### 422 — Validation (schema) errors

Returned when the JSON body doesn’t match the expected schema (missing fields, wrong types).

### 400 — Business/DB errors

Returned when the request passes schema validation but violates business rules or database constraints.


##Publci API

- **Inslall**

# macOS (Homebrew)
brew install ngrok/ngrok/ngrok

# add authtoken (Dashboard de ngrok)
ngrok config add-authtoken <TU_AUTHTOKEN>

- **make dev**
- **Open Tunnel** (ngrok http 8081)

# Page Public

- **https://5bdd077e7601.ngrok-free.app/docs**
- **https://5bdd077e7601.ngrok-free.app/healthz**
- **https://5bdd077e7601.ngrok-free.app/metrics/q_hires?year=2021**
- **https://5bdd077e7601.ngrok-free.app/metrics/top_departments?year=2021**
