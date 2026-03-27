WITH user_mentor_sessions AS (
    SELECT
        s.user_id,
        s.mentor_id,
        s.started_at,
        ROW_NUMBER() OVER (
            PARTITION BY s.user_id, s.mentor_id
            ORDER BY s.started_at
        ) AS session_num
    FROM {{ ref('fct_sessions') }} s
),

first_sessions AS (
    SELECT * FROM user_mentor_sessions WHERE session_num = 1
),

second_sessions AS (
    SELECT * FROM user_mentor_sessions WHERE session_num = 2
),

rebooking_stats AS (
    SELECT
        f.mentor_id,
        COUNT(DISTINCT f.user_id) AS total_user_mentor_pairs,
        COUNT(DISTINCT CASE
            WHEN s.started_at IS NOT NULL
                AND s.started_at <= f.started_at + INTERVAL 30 DAY
            THEN f.user_id
        END) AS total_rebooked
    FROM first_sessions f
    LEFT JOIN second_sessions s
        ON f.user_id = s.user_id
        AND f.mentor_id = s.mentor_id
    GROUP BY f.mentor_id
),

session_agg AS (
    SELECT
        mentor_id,
        MIN(started_at) AS first_session_at,
        MAX(started_at) AS last_session_at,
        COUNT(*) AS cumulative_sessions
    FROM {{ ref('fct_sessions') }}
    GROUP BY mentor_id
)

SELECT
    sa.mentor_id,
    m.tier,
    r.total_user_mentor_pairs,
    r.total_rebooked,
    ROUND(
        r.total_rebooked * 100.0 / NULLIF(r.total_user_mentor_pairs, 0),
        1
    ) AS rebooking_rate,
    sa.first_session_at,
    sa.last_session_at,
    sa.cumulative_sessions,
    ROUND(
        sa.cumulative_sessions * 1.0
        / DATE_DIFF('day', sa.first_session_at, sa.last_session_at + INTERVAL '1 day'),
        2
    ) AS avg_sessions_per_day
FROM session_agg sa
JOIN {{ ref('dim_mentors') }} m ON sa.mentor_id = m.mentor_id
LEFT JOIN rebooking_stats r ON sa.mentor_id = r.mentor_id
