# Pack Mentorship Marketplace — Local Data Warehouse

A local mini-warehouse that ingests messy multi-source data (Postgres export, JSON event stream, manual CSV), models it into a dim/fact schema, runs data quality checks, and answers the CEO's question: **Are Gold-tier mentors actually driving better retention?**

> [!NOTE]
> This branch contains my approach adhering to the test's premise. For an opinionated and more extense implementation (following best practices and a simple modeling framework+documentation+BI stack), please check out the [dbt version](https://github.com/PatFitzner/pack-test/tree/dbt_version) branch.


> [!IMPORTANT]  
> You need Docker to run this locally. Check the [Docker docs](https://docs.docker.com/engine/install/) for instructions if you don't have it.

## How to Run

```bash
docker compose up -d --build

# Inside the container, run the pipeline in order:
docker compose exec warehouse python -m src.ingest      # Load and clean raw data
docker compose exec warehouse python -m src.transform   # Build dim/fact models
docker compose exec warehouse python -m src.validate    # Run data quality checks
docker compose exec warehouse python -m src.analyze     # Produce rebooking rate analysis
```
> [!WARNING]
> This will create a lot of files in this directory tree. The `clean.sh` script is there to clear it all up once you are done!

```bash
# Clean up Docker mess
./clean.sh

# Stop containers

docker compose down
```

## Directory Structure

```
├── data/                  # As requested, here live the source data provided with the test
├── models/                # SQL model definitions
│   ├── dim_users.sql
│   ├── dim_mentors.sql
│   ├── fct_sessions.sql
│   └── fct_booking_events.sql
├── src/                   # As requested, too.
│   ├── db.py              # DuckDB connection helper
│   ├── ingest.py          # Raw ingestion with dedup and type coercion
│   ├── transform.py       # Executes SQL models in dependency order
│   ├── validate.py        # Data quality checks (3 checks)
│   └── analyze.py         # Rebooking rate analysis
├── output/                # DuckDB database file (it won't exist until you run this processes). 
├── Dockerfile             # Python container (warehouse/ingestion)
├── docker-compose.yml
├── clean.sh               # Reset repo to pre-build state
└── requirements.txt
```

---

## Architectural Decision Record

### Why DuckDB?

The premise calls for a local data warehouse. My first instinct is to spin up a PostgreSQL container with a pgAdmin instance for graphical interaction, but the premise mentions DuckDB, and it works perfectly fine as well:

- **Analytical SQL engine** — columnar storage with native `read_csv_auto()` and `read_json_auto()`, so ingestion is a single SQL statement per source. No pandas, no custom parsers.
- **Zero infrastructure** — No extra containers, just a python lib.
- **Modern SQL dialect** — window functions, `FILTER` clauses, `DATE_DIFF`, CTEs — everything needed for the session reconstruction and analysis queries without workarounds.

SQLite was the other option. I chose DuckDB because you mention that we want to eventually migrate to Snowflake, and both Snowflake and DuckDB are columnar with vectorized execution, while SQLite is row-oriented and optimized for OLTP.

### Why did I model this way?

The premise already requested **`dim_users`** and **`dim_mentors`**, which were a no-brainer. **`fct_sessions`** was also requested, but I decided to split it into 2 models: the already mentioned **`fct_sessions`**, and an additional **`fct_booking_events`**.

I have decided to do this because the data provided in `booking_events.json` is, as its name suggests, an event stream (presumably from a CDP). The term "session" is infamously ambiguous in our industry, referring both to a browsing/platform usage session, as well as to, in our case, a mentoring session. I've been bit by this before, and it is a real pain. To address this ambiguity, we differentiate two types of booking_event: those that constitute mentoring session boundaries (`session_started` and `session_ended`), and those that constitute user or mentor actions in the platform (booking requests, confirmations, cancellations...). This way, each table includes facts related to each other by their conceptual meaning, rather than by the system they happened to come from.

- **`dim_users`** and **`dim_mentors`** — clean reference tables. Deduplication and type coercion happen at ingestion so dimensions are trustworthy join targets.
- **`fct_sessions`** — the hard part. Reconstructs sessions from an event stream using FIFO matching: `session_started` and `session_ended` events are paired per (user, mentor) by chronological order. Missing `session_ended` events default to 30-minute duration per the spec.
- **`fct_booking_events`** — booking lifecycle events (requested, confirmed, cancelled) separated from session events. This keeps the fact tables focused: one for sessions, one for bookings.

---

## Future-State Strategy

If building this for real on AWS/Snowflake next week:

### Data Warehouse: Snowflake if we must, ClickHouse/PostgreSQL if we can

Honestly, I am choosing Snowflake because it is what you mentioned in the test premise. If it was up to me, I'd use either ClickHouse or PostgreSQL - Open Source systems that do not lock us in to a vendor, and perform excellently.

### Ingestion: dlthub or Airbyte

The Postgres user table and the third-party booking tool JSON would each get a managed connector. Airbyte handles CDC (change data capture), schema drift detection, and incremental syncs. The manual mentor tier CSV would go into a Google Sheet with a dlthub connector, so the Ops team keeps their familiar workflow while we get automated syncs. I am guessing based on the job opening that the booking_events data comes from PostHog, which happens to have integration with both Airbyte and dlthub.

### Transformation: dbt

dbt is the industry standard for data modeling, and a tool I bring significant expertise with. The benefits of treating our data model like a software project (version controlled, tested, checked by CI, and documented) cannot be overstated.

The business logic complexity that is inherent to any mature business is simply unmanageable without a proper modeling framework.

### Data Quality: dbt Tests + Great Expectations

The three validation checks in `validate.py` become dbt tests — `not_null`, `accepted_values`, custom SQL tests. For more complex validation (distribution checks, anomaly detection, cross-source reconciliation), Great Expectations provides a framework with built-in expectation libraries.

Initially, though, built-in dbt tests provide an excellent baseline without any build overhead.

### Orchestration: Airflow or Dagster

Right now the pipeline is "run these four scripts in order." In production, you need: scheduled runs, dependency management, failure alerts, backfill support, and observability. Airflow is the established choice (larger ecosystem, more hiring pool), and the one I have experience with. Dagster is the modern choice (asset-based, built-in dbt integration), but I have no experience with it.

I would suggest Airflow as a first step, as it is not explicitly built for data, therefore we could orchestrate other business processes and trigger our data pipelines with awareness of these business process' state.

### BI Layer: Metabase

The CEO shouldn't be asking an engineer for the rebooking rate. A BI tool on top of our data model lets stakeholders self-serve. Metabase is simple to set up and good enough for most teams. Also, it is free and open source. If our complexity justifies it, we can evaluate more powerful solutions (such as Looker or PowerBI), but to get up and running fast and cheap, Metabase is more than enough and by no means a bad tool.

---

## The Answer

**Are Gold-tier mentors delivering better retention?**

**Yes.** Gold mentors have a 61.9% rebooking rate, compared to 38.6% for Silver and 0% for Bronze.

### Rebooking Rate by Mentor Tier

| Tier   | Users | Rebooked | Rate  |
|--------|------:|--------:|------:|
| Gold   |    42 |      26 | 61.9% |
| Silver |    57 |      22 | 38.6% |
| Bronze |    33 |       0 |  0.0% |

*Rebooking = user booked a second session within 30 days of their first.*

### Key Findings

1. **Gold mentors drive 1.6x the rebooking rate of Silver** (61.9% vs 38.6%). The tier system is working — top-tier mentors measurably retain users.

2. **Same-mentor and any-mentor rebooking rates are identical.** Users who rebook are going back to the *same* mentor, not switching. This suggests users form loyalty to specific mentors, which has implications for mentor capacity planning and matching algorithms.

3. **Bronze has 0% rebooking.** No Bronze-tier user-mentor pair produced a second session. This could indicate a quality threshold below which users churn entirely, or it could reflect sample size (33 pairs). Worth investigating with more data.
