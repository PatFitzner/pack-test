FROM python:3.12-slim

WORKDIR /app/dbt

RUN pip install --no-cache-dir dbt-duckdb

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["sleep", "infinity"]
