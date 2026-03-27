import sys
from src.db import get_connection


def check_negative_durations(con):
    """WARNING: Alert if any session has negative duration."""
    rows = con.execute("""
        SELECT session_id, user_id, mentor_id, started_at, ended_at, duration_minutes
        FROM fct_sessions
        WHERE duration_minutes < 0
    """).fetchall()

    if rows:
        print(f"WARNING: {len(rows)} session(s) with negative duration:")
        for row in rows:
            print(f"  {row}")
        return False
    else:
        print("PASS: No sessions with negative duration")
        return True


def check_orphan_bookings(con):
    """FAIL: Pipeline fails if >5% of booking events have no matching user."""
    result = con.execute("""
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (
                WHERE e.user_id NOT IN (SELECT user_id FROM dim_users)
            ) AS orphans
        FROM fct_booking_events e
    """).fetchone()

    total, orphans = result
    rate = (orphans / total * 100) if total > 0 else 0

    if rate > 5:
        print(f"FAIL: {orphans}/{total} orphan bookings ({rate:.1f}%) exceeds 5% threshold")
        return False
    else:
        print(f"PASS: {orphans}/{total} orphan bookings ({rate:.1f}%) within 5% threshold")
        return True


def check_session_mentor_integrity(con):
    """WARNING: Alert if sessions reference non-existent mentors."""
    rows = con.execute("""
        SELECT s.session_id, s.mentor_id
        FROM fct_sessions s
        WHERE s.mentor_id NOT IN (SELECT mentor_id FROM dim_mentors)
    """).fetchall()

    if rows:
        print(f"WARNING: {len(rows)} session(s) reference unknown mentors:")
        for row in rows:
            print(f"  {row}")
        return False
    else:
        print("PASS: All sessions reference valid mentors")
        return True


def validate():
    con = get_connection()

    print("Running data quality checks...\n")

    check_negative_durations(con)
    orphans_ok = check_orphan_bookings(con)
    check_session_mentor_integrity(con)

    con.close()

    if not orphans_ok:
        print("\nValidation FAILED: orphan threshold exceeded")
        sys.exit(1)

    print("\nValidation complete.")


if __name__ == "__main__":
    validate()
