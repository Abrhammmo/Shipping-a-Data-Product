-- Test to ensure no data loss: row count in fact table should match staging table
SELECT 1
WHERE (SELECT COUNT(*) FROM {{ ref('fct_messages') }}) != (SELECT COUNT(*) FROM {{ ref('stg_telegram_messages') }})