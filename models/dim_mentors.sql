CREATE OR REPLACE TABLE dim_mentors AS
SELECT
    mentor_id,
    tier,
    hourly_rate
FROM raw_mentors;
