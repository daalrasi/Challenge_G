#!/usr/bin/env bash
set -euo pipefail
BASE="http://localhost:8081"
curl -fsS -F "file=@/Users/ASILVA/Downloads/data_challenge_files/departments.csv" "$BASE/upload_csv?table=departments"
curl -fsS -F "file=@/Users/ASILVA/Downloads/data_challenge_files/jobs.csv" "$BASE/upload_csv?table=jobs"
echo
echo "Seed OK"
