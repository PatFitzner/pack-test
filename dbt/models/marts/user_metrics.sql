WITH session_gaps AS (
    SELECT
        user_id,
        started_at,
        DATE_DIFF(
            'day',
            LAG(started_at) OVER (PARTITION BY user_id ORDER BY started_at),
            started_at
        ) AS days_since_prev
    FROM {{ ref('fct_sessions') }}
)

SELECT
    s.user_id,
    MIN(s.started_at) AS first_session_at,
    MAX(s.started_at) AS last_session_at,
    COUNT(*) AS cumulative_sessions,
    ROUND(AVG(s.duration_minutes), 1) AS avg_session_duration_minutes,
    ROUND(AVG(g.days_since_prev), 1) AS avg_days_between_sessions
FROM {{ ref('fct_sessions') }} s
LEFT JOIN session_gaps g
    ON s.user_id = g.user_id
    AND s.started_at = g.started_at
GROUP BY s.user_id
