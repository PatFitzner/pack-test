#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Use the warehouse container to remove root-owned build artifacts
echo "Removing build artifacts via container..."
docker compose -f "$REPO_ROOT/docker-compose.yml" run --rm \
  -v "$REPO_ROOT/output:/app/output" \
  --no-deps warehouse bash -c "
    rm -f /app/output/warehouse.duckdb /app/output/warehouse.duckdb.wal
  " 2>/dev/null || true

echo "Stopping containers..."
docker compose -f "$REPO_ROOT/docker-compose.yml" down 2>/dev/null || true

echo "Removing Python artifacts..."
find "$REPO_ROOT" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -name '*.pyc' -delete 2>/dev/null || true

echo "Clean complete."
