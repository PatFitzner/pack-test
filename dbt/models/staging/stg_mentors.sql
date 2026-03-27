SELECT
    mentor_id,
    tier,
    hourly_rate
FROM {{ source('raw', 'raw_mentors') }}
