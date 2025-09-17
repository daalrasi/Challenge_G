# Globant Challenge Daniel Silva
Deployment Challenge_G

This project implements the Globant Challenge Daniel Silva using 
**FastAPI, PostgreSQL, and Docker**.  
It used for data ingestion from CSV files, batch inserts with validation, and analytical queries for reporting.  


## Tech Stack

- **FastAPI**
- **PostgreSQL**
- **Docker Compose**
- **SQLAlchemy**
- **Pydantic**
  


## Running the Application

requeriments.txt: This file has content related to requirements to external packages needed to run API functionalities.

Clone the repository and start the services with Docker Compose:

<img width="1470" height="832" alt="Screenshot 2025-09-17 at 12 39 54 PM" src="https://github.com/user-attachments/assets/2175e8b6-06ab-4b36-8a2e-f56dcec3bd7e" />


bash
docker compose up --build



The following services will be available:

•	API: http://localhost:8081/docs

•	Database: PostgreSQL exposed at localhost:5432


## API Endpoints

- **verify the API is running**
- **curl http://localhost:8081/healthz**

Response:
{"status":"ok"}


<img width="1461" height="842" alt="Screenshot 2025-09-17 at 2 34 50 PM" src="https://github.com/user-attachments/assets/18e3469c-e24e-45d5-8742-dff62e552be5" />

## CSV Upload
Upload data directly into the target tables: departments, jobs, hired_employees.

Example – Upload:

curl -F "file=@departments.csv" "http://localhost:8081/upload_csv?table=departments"

Response:
{"inserted_or_updated": 10, "skipped_rows": 0}

<img width="1425" height="831" alt="Screenshot 2025-09-17 at 2 36 18 PM" src="https://github.com/user-attachments/assets/5c05d886-b835-4f2a-b609-4d988c884e0f" />


Tables supported:
- **departments(id, department)**
-	**jobs(id, job)**
-	**hired_employees(id, name, datetime, department_id, job_id)**
 

## POST /insert_batch

- **Batch insert (JSON)**  
  http://localhost:8081/docs#/Ingestion/insert_batch_insert_batch_post

- **batch_1000.json -- Example Especific 1000**
- **batch_1001.json -- Example more 1000**
  
<img width="1434" height="834" alt="Screenshot 2025-09-17 at 2 37 17 PM" src="https://github.com/user-attachments/assets/deb59861-0fab-4f59-8355-c35e45c4dfd2" />

  
schema json

{
  "items": [
    { "id": 50021, "name": "User A", "datetime": "2021-02-03T08:00:00", "department_id": 1, "job_id": 1 },
    { "id": 50022, "name": "User B", "datetime": "2021-02-04T09:00:00", "department_id": 2, "job_id": 2 }
  ]
}

<img width="1456" height="813" alt="Screenshot 2025-09-17 at 2 38 34 PM" src="https://github.com/user-attachments/assets/4be3ef77-1113-4ec0-8d80-b685604a11a2" />



## Query SQL

Generate the metrics quarterly hires

## Number of Employees

- **Quarterly Hires**  
  http://localhost:8081/docs#/Metrics/q_hires_metrics_q_hires_get

  <img width="1428" height="839" alt="Screenshot 2025-09-17 at 2 39 25 PM" src="https://github.com/user-attachments/assets/807b7020-5691-4204-b3f2-81e5c032c50e" />


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

  <img width="1419" height="835" alt="Screenshot 2025-09-17 at 2 40 10 PM" src="https://github.com/user-attachments/assets/d914e3b1-cc1d-4ddb-a233-c612be465f7b" />


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

<img width="1240" height="471" alt="Screenshot 2025-09-17 at 3 54 06 PM" src="https://github.com/user-attachments/assets/13df3ef3-79a9-4501-8c39-cb2365cdae20" />


- **make dev**
- **Open Tunnel** (ngrok http 8081)

# Page Public

<img width="1457" height="831" alt="Screenshot 2025-09-17 at 2 41 29 PM" src="https://github.com/user-attachments/assets/6d4d004b-c4ff-4b3e-bd39-b51effa8fb88" />

- **https://4023a63d4740.ngrok-free.app/docs**
- **https://4023a63d4740.ngrok-free.app/healthz**
- **https://4023a63d4740.ngrok-free.app/metrics/q_hires?year=2021**
- **https://4023a63d4740.ngrok-free.app/metrics/top_departments?year=2021**
