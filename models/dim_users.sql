CREATE OR REPLACE TABLE dim_users AS
SELECT
    user_id,
    company_id,
    signup_date,
    status
FROM raw_users;
