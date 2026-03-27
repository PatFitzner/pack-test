CREATE OR REPLACE TABLE fct_sessions AS
WITH starts AS (
    SELECT
        event_id AS session_id,
        user_id,
        mentor_id,
        event_timestamp AS started_at,
        LEAD(event_timestamp) OVER (
            PARTITION BY user_id, mentor_id
            ORDER BY event_timestamp
        ) AS next_started_at
    FROM raw_booking_events
    WHERE event_type = 'session_started'
),
ends AS (
    SELECT
        user_id,
        mentor_id,
        event_timestamp AS ended_at
    FROM raw_booking_events
    WHERE event_type = 'session_ended'
)
SELECT
    s.session_id,
    s.user_id,
    s.mentor_id,
    s.started_at,
    e.ended_at,
    COALESCE(
        DATE_DIFF('minute', s.started_at, e.ended_at),
        30
    ) AS duration_minutes
FROM starts s
LEFT JOIN ends e
    ON s.user_id = e.user_id
    AND s.mentor_id = e.mentor_id
    AND e.ended_at > s.started_at
    AND (s.next_started_at IS NULL OR e.ended_at < s.next_started_at);
