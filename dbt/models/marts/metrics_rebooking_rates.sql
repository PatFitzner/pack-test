SELECT
    tier,
    COUNT(*) AS total_mentors,
    SUM(total_user_mentor_pairs) AS total_user_mentor_pairs,
    SUM(total_rebooked) AS total_rebooked,
    ROUND(
        SUM(total_rebooked) * 100.0 / NULLIF(SUM(total_user_mentor_pairs), 0),
        1
    ) AS rebooking_rate_pct
FROM {{ ref('mentor_metrics') }}
GROUP BY tier
ORDER BY tier
