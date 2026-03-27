from src.db import get_connection


def ingest():
    con = get_connection()

    # --- Users ---
    # Deduplicate exact duplicate rows, cast user_id to VARCHAR
    con.execute("""
        CREATE OR REPLACE TABLE raw_users AS
        SELECT DISTINCT
            CAST(user_id AS VARCHAR) AS user_id,
            company_id,
            CAST(signup_date AS DATE) AS signup_date,
            status
        FROM read_csv_auto('/app/data/users_db_export.csv')
    """)
    user_count = con.execute("SELECT COUNT(*) FROM raw_users").fetchone()[0]
    raw_count = con.execute(
        "SELECT COUNT(*) FROM read_csv_auto('/app/data/users_db_export.csv')"
    ).fetchone()[0]
    print(f"Users: loaded {raw_count} rows, deduplicated to {user_count}")

    # --- Booking Events ---
    # Cast user_id to VARCHAR for join consistency.
    # DuckDB's read_json_auto infers mixed int/string user_id as JSON type.
    # CAST(JSON AS VARCHAR) preserves literal quotes on string values,
    # so we strip them with REPLACE to get clean VARCHAR values.
    con.execute("""
        CREATE OR REPLACE TABLE raw_booking_events AS
        SELECT
            event_id,
            REPLACE(CAST(user_id AS VARCHAR), '"', '') AS user_id,
            mentor_id,
            CAST("timestamp" AS TIMESTAMP) AS event_timestamp,
            event_type
        FROM read_json_auto('/app/data/booking_events.json')
    """)
    event_count = con.execute("SELECT COUNT(*) FROM raw_booking_events").fetchone()[0]
    print(f"Booking events: loaded {event_count} rows")

    # --- Mentors ---
    con.execute("""
        CREATE OR REPLACE TABLE raw_mentors AS
        SELECT * FROM read_csv_auto('/app/data/mentor_tiers.csv')
    """)
    mentor_count = con.execute("SELECT COUNT(*) FROM raw_mentors").fetchone()[0]
    print(f"Mentors: loaded {mentor_count} rows")

    # --- Verify mentor_id format consistency ---
    mismatch = con.execute("""
        SELECT COUNT(*) FROM raw_booking_events e
        WHERE e.mentor_id NOT IN (SELECT mentor_id FROM raw_mentors)
    """).fetchone()[0]
    if mismatch == 0:
        print("Mentor ID format: consistent across sources (no coercion needed)")
    else:
        print(f"WARNING: {mismatch} booking events reference unknown mentor_ids")

    con.close()
    print("Ingestion complete.")


if __name__ == "__main__":
    ingest()
