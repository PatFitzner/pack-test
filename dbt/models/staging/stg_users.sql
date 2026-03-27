SELECT DISTINCT
    user_id,
    company_id,
    signup_date,
    status
FROM {{ source('raw', 'raw_users') }}
