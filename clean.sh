#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Use the dbt container to remove root-owned build artifacts
echo "Removing build artifacts via container..."
docker compose -f "$REPO_ROOT/docker-compose.yml" run --rm \
  -v "$REPO_ROOT/dbt:/app/dbt" \
  -v "$REPO_ROOT/output:/app/output" \
  --no-deps dbt bash -c "
    rm -rf /app/dbt/target /app/dbt/logs /app/dbt/dbt_packages
    rm -f  /app/dbt/.user.yml /app/dbt/package-lock.yml
    rm -rf /app/dbt/reports/.evidence /app/dbt/reports/build
    rm -f  /app/dbt/reports/package-lock.json
    rm -f  /app/output/warehouse.duckdb /app/output/warehouse.duckdb.wal
  " 2>/dev/null || true

echo "Stopping containers and removing volumes..."
docker compose -f "$REPO_ROOT/docker-compose.yml" down -v 2>/dev/null || true

echo "Removing Python artifacts..."
find "$REPO_ROOT" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -name '*.pyc' -delete 2>/dev/null || true

echo "Clean complete."
