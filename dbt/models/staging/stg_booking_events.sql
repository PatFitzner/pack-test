SELECT
    event_id,
    user_id,
    mentor_id,
    event_timestamp,
    event_type
FROM {{ source('raw', 'raw_booking_events') }}
WHERE event_type IN ('booking_requested', 'booking_confirmed', 'booking_cancelled')
