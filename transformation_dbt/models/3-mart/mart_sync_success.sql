with sync_status as (select * from {{ ref('core_airbyte_sync_status') }} )
SELECT
    source2destination_name,
    count(*) AS total_attempts,
    coalesce(sum(CASE WHEN attempt_succeeded THEN 1 ELSE 0 END), 0) AS attempt_succeeded,
    coalesce(sum(CASE WHEN attempt_failed THEN 1 ELSE 0 END), 0) AS attempt_failed,
    coalesce(sum(CASE WHEN attempt_succeeded_first_attempt THEN 1 ELSE 0 END), 0) AS attempt_succeeded_first_attempt,
    coalesce(sum(CASE WHEN attempt_succeeded THEN 1 ELSE 0 END), 0) * 100.0 / count(*) AS success_rate,
    coalesce(sum(CASE WHEN attempt_succeeded_first_attempt THEN 1 ELSE 0 END), 0) * 100.0 / count(*) AS success_rate_first_attempt,
    coalesce(sum(CASE WHEN attempt_running THEN 1 ELSE 0 END), 0) AS attempt_running,
    sum(attempt_duration) AS sum_attempt_duration,
    sum(volume_rows) AS sum_volume_rows,
    sum(volume_mb) AS sum_volume_mb

FROM sync_status

GROUP BY source2destination_name
