
{{ config(
    cluster_by = ["connection_id"],
    partition_by = {"field": "dt", "data_type": "date", "granularity": "day"}
) }}
with

jobs as (

    select * from {{ ref('stg_airbyte__jobs') }}

),



connection as (

    select * from {{ ref('stg_airbyte__connection') }}

),

actor as (

    select * from {{ ref('stg_airbyte__actor') }}

),

attempts as (

    select * from {{ ref('stg_airbyte__attempts') }}

),

attempts_jobs as (

    select * from {{ ref('join_cloud_attempts_jobs') }}

),

attempt_data as (


    select
        attempts.sync_unique_key,
        jobs.status,
        attempts.volume_rows,
        attempts.volume_mb,  -- a.failure_type, a.failure_origin, a.internal_message, a.external_message,
        actor_source.connector_name as source_connector_name,
        --sc.connector_type as source_connector_type,
        actor_destination.connector_name as destination_connector_name,
        jobs.created_at as sync_started,
        --dc.connector_type as destination_connector_type,
        jobs.updated_at as sync_updated,
        attempts_jobs.job_id,
        attempts_jobs.config_type,
        attempts_jobs.jobs_created_at,
        attempts_jobs.event_at,
        attempts_jobs.jobs_cpu_request,
        attempts_jobs.jobs_memory_request,
        attempts_jobs.jobs_source_docker_image,
        attempts_jobs.jobs_destination_docker_image,
        attempts_jobs.ended_at,
        attempts_jobs.standard_sync_summary,
        attempts_jobs.attempt_volume_mb,
        attempts_jobs.attempt_volume_rows,
        attempts_jobs.failure_reasons,
        attempts_jobs.count_state_messages_from_source,
        attempts_jobs.count_state_messages_from_destination,
        attempts_jobs.max_seconds_before_source_state_message_emitted,
        attempts_jobs.max_seconds_between_state_message_emit_and_commit,
        attempts_jobs.attempt_id,
        attempts_jobs.attempt_ended,
        attempts_jobs.attempt_duration,
        attempts_jobs.attempt_running,
        attempts_jobs.attempt_failed,
        attempts_jobs.attempt_succeeded_first_attempt,
        attempts_jobs.attempt_succeeded,
        actor_source.connector_name || '->' || actor_destination.connector_name as source2destination_name

    from jobs
    left outer join attempts on jobs.job_id = attempts.job_id
    left outer join connection on jobs.connection_id = connection.connection_id
    left outer join actor as actor_source on connection.source_id = actor_source.connector_id
    left outer join actor as actor_destination on connection.destination_id = actor_destination.connector_id
    left outer join attempts_jobs on attempts.sync_unique_key = attempts_jobs.sync_unique_key

)

select * from attempt_data
