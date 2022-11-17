{{ config(
    cluster_by = ["job_id", "attempt_id"],
    partition_by = {"field": "dt", "data_type": "date", "granularity": "day"}
) }}
with
attempts_raw_data as (select * from {{ ref('stg_airbyte__attempts') }}
),

jobs_raw_data as (select * from {{ ref('stg_airbyte__jobs') }}
),

--in BQ except function is used with `except(loaded_at, failure_reason)
attempts_data as (select distinct
    id,
    dt,
    job_id,
    "output",
    status,
    log_path,
    attempt_id,
    temporal_workflow_id,
    standard_sync_summary::text,
    volume_rows,
    volume_mb,
    sync_unique_key,
    count_state_messages_from_source,
    count_state_messages_from_destination,
    max_seconds_before_source_state_message_emitted,
    mean_seconds_before_source_state_message_emitted,
    max_seconds_between_state_message_emit_and_commit,
    ean_seconds_between_state_message_emit_and_commit,
    failure_type,
    failure_origin,
    internal_message,
    external_message,
    created_at,
    updated_at,
    ended_at
    from attempts_raw_data
),

attempts_incl_row_num as ( select
        sync_unique_key,
        job_id,
        attempt_id,
        failure_reasons,
        dt,
        row_number() over (
            partition by sync_unique_key, job_id, attempt_id, temporal_workflow_id order by dt desc, updated_at desc, ended_at desc, loaded_at desc
        ) as seq
    from attempts_raw_data
),

attempts_failure_reasons_data as (
    select
        sync_unique_key,
        job_id,
        attempt_id,
        failure_reasons,
        dt
    from attempts_incl_row_num
    where seq = 1
),

jobs_data as (
    select distinct
        --except(loaded_at, operation_sequence, cpu_request, memory_request)
        job_id,
        connection_id,
        status,
        config_type,
        namespace_definition,
        namespace_format,
        prefix,
        source_configuration,
        destination_configuration,
        configured_airbyte_catalog,
        source_docker_image,
        destination_docker_image,
        state,
        resource_requirements,
        created_at,
        updated_at,
        dt,
        case when cpu_request = '{}' then null else cpu_request end as cpu_request,
        case when memory_request = '{}' then null else memory_request end as memory_request
    from jobs_raw_data
),

attempt_columns as (
    select
        attempts_data.sync_unique_key,
        jobs_data.connection_id,
        jobs_data.job_id,
        jobs_data.config_type,
        -- see https://github.com/airbytehq/airbyte/issues/9796#issuecomment-1034909338
        attempts_data.dt,

        jobs_data.created_at as jobs_created_at,

        attempts_data.created_at as event_at,
        jobs_data.cpu_request as jobs_cpu_request,

        jobs_data.memory_request as jobs_memory_request,
        jobs_data.source_docker_image as jobs_source_docker_image,

        jobs_data.destination_docker_image as jobs_destination_docker_image,
        attempts_data.ended_at,

        attempts_data.standard_sync_summary,
        attempts_data.volume_mb as attempt_volume_mb,
        attempts_data.volume_rows as attempt_volume_rows,
        attempts_failure_reasons_data.failure_reasons,

        -- Checkpoint Metrics
        /* attempts_data.number_of_streams, */
        attempts_data.count_state_messages_from_source,
        attempts_data.count_state_messages_from_destination,
        attempts_data.max_seconds_before_source_state_message_emitted,
        /* attempts_data.mean_seconds_before_source_state_message_emitted, */
        attempts_data.max_seconds_between_state_message_emit_and_commit,
        /* attempts_data.mean_seconds_between_state_message_emit_and_commit, */

        (attempts_data.attempt_id + 1) as attempt_id,
        attempts_data.ended_at is not null as attempt_ended,
        extract(epoch from (attempts_data.ended_at - attempts_data.created_at)) as attempt_duration,
        (attempts_data.status = 'running') as attempt_running,
        (attempts_data.status = 'failed') as attempt_failed,
        (attempts_data.status = 'succeeded' and attempts_data.attempt_id = 0) as attempt_succeeded_first_attempt,
        (attempts_data.status = 'succeeded') as attempt_succeeded

    from attempts_data

    left join attempts_failure_reasons_data
        on attempts_data.job_id = attempts_failure_reasons_data.job_id
            and attempts_data.attempt_id = attempts_failure_reasons_data.attempt_id
            and attempts_data.sync_unique_key = attempts_failure_reasons_data.sync_unique_key
            and attempts_data.dt = attempts_failure_reasons_data.dt

    inner join jobs_data
        on attempts_data.job_id = jobs_data.job_id
            and jobs_data.dt >= attempts_data.dt - interval '4' day
)

select * from attempt_columns
