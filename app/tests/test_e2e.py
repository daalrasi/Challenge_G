import os
import time
import json
import requests

API = os.getenv("API_URL", "http://localhost:8081")

def wait_for(url, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Timeout waiting for {url}")

def test_health_and_seed_and_metrics():
    # Start Api
    wait_for(f"{API}/healthz")
    r = requests.get(f"{API}/healthz")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

    # Seed intial
    files = {"file": ("departments.csv", b"1,Engineering\n2,HR\n")}
    r = requests.post(f"{API}/upload_csv?table=departments", files=files)
    assert r.status_code == 200, r.text

    files = {"file": ("jobs.csv", b"1,Data Engineer\n2,Recruiter\n")}
    r = requests.post(f"{API}/upload_csv?table=jobs", files=files)
    assert r.status_code == 200, r.text

    # Batch Correct (≤1000)
    batch = {
        "items": [
            {"id": 91001, "name": "Alice", "datetime": "2021-02-01T08:00:00", "department_id": 1, "job_id": 1},
            {"id": 91002, "name": "Bob",   "datetime": "2021-03-01T09:00:00", "department_id": 2, "job_id": 2},
        ]
    }
    r = requests.post(f"{API}/insert_batch", json=batch)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "inserted_or_updated" in data and data["inserted_or_updated"] == 2

    # Metrics
    r = requests.get(f"{API}/metrics/q_hires", params={"year": 2021})
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)

    r = requests.get(f"{API}/metrics/top_departments", params={"year": 2021})
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)

def test_batch_too_large_returns_400():
    # payload > 1001 items rules enpint 400
    items = [
        {"id": 100000 + i, "name": f"U{i}", "datetime": "2021-01-01T10:00:00", "department_id": 1, "job_id": 1}
        for i in range(1001)
    ]
    payload = {"items": items}
    r = requests.post(f"{API}/insert_batch", json=payload)
    assert r.status_code == 400, r.text
    assert "items length must be between 1 and 1000" in r.text

