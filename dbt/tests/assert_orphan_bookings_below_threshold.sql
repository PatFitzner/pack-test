{{ config(severity='error') }}

WITH orphan_stats AS (
    SELECT
        COUNT(*) AS total,
        COUNT(*) FILTER (
            WHERE user_id NOT IN (SELECT user_id FROM {{ ref('dim_users') }})
        ) AS orphans
    FROM {{ ref('fct_booking_events') }}
)

SELECT total, orphans, orphans * 100.0 / total AS orphan_rate
FROM orphan_stats
WHERE orphans * 100.0 / total > 5
