WITH source AS (
    SELECT * FROM raw.telegram_messages
)

SELECT
    message_id,
    channel_name,
    CAST(message_date AS TIMESTAMP) AS message_date,
    message_text,
    LENGTH(message_text) AS message_length,
    COALESCE(views, 0) AS view_count,
    COALESCE(forwards, 0) AS forward_count,
    has_media AS has_image,
    image_path
FROM source
WHERE message_text IS NOT NULL
