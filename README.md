# Pack Mentorship test

This branch (**dbt-version**) takes a more opinionated approach to our situation. Instead of simply building the minimum viable model to answer one specific question, we try to predict and infer our stakeholder's needs. For that, we extend our data model to provide a wider range of metris on our key business entities. This way, we don't give just a verbal ad-hoc answer to a question, but instead we provide a visual interface through which to **visualize** and **understand** the information that constitutes our answer. After answering the question "Are our 'Top Tier' mentors actually delivering better retention than the standard ones?" we can expect to hear a "why?" and a "by how much?" almost 100% of the time

## How to Run

```bash
docker compose up -d --build

# Step 1: Ingest raw data (Python)
docker compose exec warehouse python -m src.ingest

# Step 2: Build dbt models
docker compose exec dbt dbt deps
docker compose exec dbt dbt run

# Step 3: Run data quality tests
docker compose exec dbt dbt test

# Step 4: Open the dashboard
# http://localhost:3000
```
> [!WARNING]
> This will create a lot of files in this directory tree. The `clean.sh` script is there to clear it all up once you are done!

```bash
# Clean up Docker mess
./clean.sh

# Stop containers

docker compose down
```

Evidence starts automatically with `docker compose up`. Once dbt has populated the tables, the dashboard is live at [http://localhost:3000](http://localhost:3000).

## Directory Structure

```
├── data/                          # As requested, here live the source data provided with the test
├── src/                           # As requested, too. This is thinner than master because we are running ELT, so transformations and testing live in dbt
│   ├── db.py                      # DuckDB connection helper
│   └── ingest.py                  # Raw ingestion with type casting (no transformation)
├── dbt/                           # dbt project
│   ├── models/
│   │   ├── staging/               # Views — dedup, type cleanup, session reconstruction
│   │   ├── dimension/             # Tables — clean business entities
│   │   ├── facts/                 # Tables — event/session grain
│   │   └── marts/                 # Tables — metrics and analysis
│   ├── tests/                     # Singular data quality tests
│   ├── reports/                   # Evidence dashboard project (this is our BI tool)
│   │   ├── pages/                 # Dashboard pages (Markdown + SQL + components)
│   │   └── sources/warehouse/     # DuckDB connection config
│   └── Dockerfile                 # Python + Node container (dbt + Evidence)
├── output/                        # DuckDB database file (it won't exist until you run this processes).
├── Dockerfile                     # Python container (warehouse/ingestion)
├── docker-compose.yml             # Three services: warehouse + dbt + reports
└── clean.sh                       # Reset repo to pre-build state
```

## Architectural Decision Record

### Why DuckDB?

Answered in **master** branch.

### Why dbt?

I've briefly made my case for dbt in the **master** branch, but here we can see examples of:

- **Dependency-aware DAG** — models declare their dependencies via `{{ ref() }}`, so dbt resolves execution order automatically. No hardcoded `MODEL_ORDER` list.
- **Built-in testing** — generic tests (`unique`, `not_null`, `relationships`, `accepted_values`) replace custom Python validation. Singular SQL tests handle threshold-based checks like the orphan bookings gate.
- **Documentation as code** — schema YAML files sit next to the models, keeping docs and tests co-located.
- **`store_failures: true`** — failed test results are materialized into the database for inspection, not just logged to stdout.

### Why Evidence?

To be honest, I just wanted to try it, and the fact that the visualizations are defined in plain text made it very easy to implement and ship without adding a lot of overhead.

### Why This Model Structure?

The dbt project uses four layers:

- **Staging (views)** — light transformations on raw tables. 
- **Dimension (tables)** — `dim_users` and `dim_mentors`. 
- **Facts (tables)** — `fct_sessions` (session grain with duration) and `fct_booking_events` (booking lifecycle events). 
- **Marts (tables)** — Data marts ready for external consumption. Provide specific metrics on our key business entities.

I really prefer this separation of concerns against the approach followed in the **master** branch.

## The Answer

**Are Gold-tier mentors delivering better retention?**

**Yes.** This obviously hasn't changed in this branch.

### Insights from the Models

**Session health** — 203 total sessions across 132 users. 6.4% (13 sessions) have no `session_ended` event and are flagged with `is_synthetic_ending = true`, defaulting to a 30-minute duration. The median session is 30 minutes.

**User engagement** — Users average 1.5 sessions each, with 12.2 days between sessions. This suggests most users are single-session, making that first impression critical for rebooking.

**Mentor performance by tier** — Gold mentors average 18.2 sessions each vs 11.3 for Silver and 11.0 for Bronze. Gold mentors don't just retain better — they handle more volume, suggesting the tier system reflects genuine capacity and quality differences.

**Bronze is a dead zone** — Zero rebookings across 33 user-mentor pairs and 3 mentors. This isn't a sample size issue — it's a pattern. No Bronze user came back to the same mentor within 30 days.

### Next Steps

The data supports the CEO's hypothesis. Gold mentors are the retention engine. The dashboards at `http://localhost:3000` provide interactive exploration of these metrics:

- **CEO Dashboard** — rebooking rates by tier
- **Mentor Performance** — per-mentor drill-down with tier filtering
- **User Engagement** — session distribution per user
- **Session Health** — duration distribution, synthetic ending rate, full session table
- **Session Trends** — weekly volume, hour-of-day and day-of-week patterns

Now, we have provided lasting value to our stakeholders (instead of a short answer), and we can gather feedback on it to do a next iteration, or continue to grow our data model to generate better and richer insights.