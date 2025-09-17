#!/usr/bin/env bash
set -euo pipefail
URL="${1:-http://localhost:8081/healthz}"
for i in {1..60}; do
  if curl -fsS "$URL" >/dev/null; then
    echo "Ready: $URL"
    exit 0
  fi
  sleep 1
done
echo "Timeout: $URL" >&2
exit 1
