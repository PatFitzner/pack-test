CREATE OR REPLACE TABLE fct_booking_events AS
SELECT
    event_id,
    user_id,
    mentor_id,
    event_timestamp,
    event_type
FROM raw_booking_events
WHERE event_type IN ('booking_requested', 'booking_confirmed', 'booking_cancelled');
