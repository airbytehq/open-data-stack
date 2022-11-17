with sync_status as (select * from {{ ref('core_airbyte_sync_status') }} )

select
    source2destination_name,
    date(sync_updated) as sync_updated,
    count(*) as total_attempts,
    coalesce(sum(case when attempt_succeeded then 1 else 0 end), 0) as attempt_succeeded,
    coalesce(sum(case when attempt_failed then 1 else 0 end), 0) as attempt_failed,
    coalesce(sum(case when attempt_succeeded_first_attempt then 1 else 0 end), 0) as attempt_succeeded_first_attempt,
    coalesce(sum(case when attempt_succeeded then 1 else 0 end), 0) * 100.0 / count(*) as success_rate,
    coalesce(sum(case when attempt_succeeded_first_attempt then 1 else 0 end), 0) * 100.0 / count(*) as success_rate_first_attempt,
    coalesce(sum(case when attempt_running then 1 else 0 end), 0) as attempt_running,
    sum(attempt_duration) as sum_attempt_duration,
    sum(volume_rows) as sum_volume_rows,
    sum(volume_mb) as sum_volume_mb

from sync_status

group by source2destination_name, date(sync_updated)
