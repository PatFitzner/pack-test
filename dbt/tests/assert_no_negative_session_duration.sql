{{ config(severity='warn') }}

SELECT
    session_id,
    duration_minutes
FROM {{ ref('fct_sessions') }}
WHERE duration_minutes < 0
