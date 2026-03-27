from src.db import get_connection


def analyze():
    con = get_connection()

    # --- Same-mentor rebooking rate ---
    # For each (user, mentor) pair: did the user have a 2nd session with
    # that same mentor within 30 days of their first?
    print("=" * 60)
    print("SAME-MENTOR REBOOKING RATE (by tier)")
    print("=" * 60)

    same_mentor = con.execute("""
        WITH user_mentor_sessions AS (
            SELECT
                s.user_id,
                s.mentor_id,
                m.tier,
                s.started_at,
                ROW_NUMBER() OVER (
                    PARTITION BY s.user_id, s.mentor_id
                    ORDER BY s.started_at
                ) AS session_num
            FROM fct_sessions s
            JOIN dim_mentors m ON s.mentor_id = m.mentor_id
        ),
        first_sessions AS (
            SELECT * FROM user_mentor_sessions WHERE session_num = 1
        ),
        second_sessions AS (
            SELECT * FROM user_mentor_sessions WHERE session_num = 2
        )
        SELECT
            f.tier,
            COUNT(DISTINCT f.user_id || '|' || f.mentor_id) AS total_pairs,
            COUNT(DISTINCT CASE
                WHEN s.started_at IS NOT NULL
                    AND s.started_at <= f.started_at + INTERVAL 30 DAY
                THEN f.user_id || '|' || f.mentor_id
            END) AS rebooked,
            ROUND(
                COUNT(DISTINCT CASE
                    WHEN s.started_at IS NOT NULL
                        AND s.started_at <= f.started_at + INTERVAL 30 DAY
                    THEN f.user_id || '|' || f.mentor_id
                END) * 100.0
                / COUNT(DISTINCT f.user_id || '|' || f.mentor_id),
                1
            ) AS rebooking_rate_pct
        FROM first_sessions f
        LEFT JOIN second_sessions s
            ON f.user_id = s.user_id
            AND f.mentor_id = s.mentor_id
        GROUP BY f.tier
        ORDER BY f.tier
    """).fetchall()

    print(f"{'Tier':<10} {'Pairs':>8} {'Rebooked':>10} {'Rate':>8}")
    print("-" * 40)
    for row in same_mentor:
        print(f"{row[0]:<10} {row[1]:>8} {row[2]:>10} {row[3]:>7.1f}%")

    # --- Any-mentor rebooking rate ---
    # For each user: based on the tier of their first-ever session's mentor,
    # did they have any second session within 30 days?
    print()
    print("=" * 60)
    print("ANY-MENTOR REBOOKING RATE (by first session's mentor tier)")
    print("=" * 60)

    any_mentor = con.execute("""
        WITH user_sessions AS (
            SELECT
                s.user_id,
                s.mentor_id,
                m.tier,
                s.started_at,
                ROW_NUMBER() OVER (
                    PARTITION BY s.user_id
                    ORDER BY s.started_at
                ) AS session_num
            FROM fct_sessions s
            JOIN dim_mentors m ON s.mentor_id = m.mentor_id
        ),
        first_sessions AS (
            SELECT * FROM user_sessions WHERE session_num = 1
        ),
        second_sessions AS (
            SELECT * FROM user_sessions WHERE session_num = 2
        )
        SELECT
            f.tier,
            COUNT(DISTINCT f.user_id) AS total_users,
            COUNT(DISTINCT CASE
                WHEN s.started_at IS NOT NULL
                    AND s.started_at <= f.started_at + INTERVAL 30 DAY
                THEN f.user_id
            END) AS rebooked,
            ROUND(
                COUNT(DISTINCT CASE
                    WHEN s.started_at IS NOT NULL
                        AND s.started_at <= f.started_at + INTERVAL 30 DAY
                    THEN f.user_id
                END) * 100.0
                / COUNT(DISTINCT f.user_id),
                1
            ) AS rebooking_rate_pct
        FROM first_sessions f
        LEFT JOIN second_sessions s
            ON f.user_id = s.user_id
        GROUP BY f.tier
        ORDER BY f.tier
    """).fetchall()

    print(f"{'Tier':<10} {'Users':>8} {'Rebooked':>10} {'Rate':>8}")
    print("-" * 40)
    for row in any_mentor:
        print(f"{row[0]:<10} {row[1]:>8} {row[2]:>10} {row[3]:>7.1f}%")

    con.close()
    print("\nAnalysis complete.")


if __name__ == "__main__":
    analyze()
