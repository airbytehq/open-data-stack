with source as (
    select *
    from {{ source('airbyte_local_db', 'attempts') }}
),

renamed as (
    select
        cast(id as text) as sync_unique_key,
        cast(id as {{ dbt_utils.type_int() }}) as id,
        cast(job_id as {{ dbt_utils.type_int() }}) as job_id,
        output,
        status,
        log_path,
        cast(attempt_number as {{ dbt_utils.type_int() }}) as attempt_id,
        temporal_workflow_id,

        json_extract_path(output::json, 'sync', 'standardSyncSummary') as standard_sync_summary,
        coalesce({{ json_extract_text_custom('output', ['sync', 'standardSyncSummary', 'recordsSynced'], 'integer') }},0)  as volume_rows,
        coalesce({{ json_extract_text_custom('output', ['sync', 'standardSyncSummary', 'bytesSynced'], 'float') }}  / (1024 * 1024),0) as volume_mb,

        {{ json_extract_text_custom('output', ['sync', 'output_catalog']) }} as number_of_streams,
        {{ json_extract_text_custom('output', ['sync', 'standardSyncSummary', 'totalStats', 'sourceStateMessagesEmitted'], 'integer') }} as count_state_messages_from_source,
        {{ json_extract_text_custom('output', ['sync', 'standardSyncSummary', 'totalStats', 'destinationStateMessagesEmitted'], 'integer') }} as count_state_messages_from_destination,
        {{ json_extract_text_custom('output', ['sync', 'standardSyncSummary', 'totalStats', 'maxSecondsBeforeSourceStateMessageEmitted'], 'integer') }} as max_seconds_before_source_state_message_emitted,
        {{ json_extract_text_custom('output', ['sync', 'standardSyncSummary', 'totalStats', 'meanSecondsBeforeSourceStateMessageEmitted'], 'integer') }} as mean_seconds_before_source_state_message_emitted,
        {{ json_extract_text_custom('output', ['sync', 'standardSyncSummary', 'totalStats', 'maxSecondsBetweenStateMessageEmittedandCommitted'], 'integer') }} as max_seconds_between_state_message_emit_and_commit,
    {{ json_extract_text_custom('output', ['sync', 'standardSyncSummary', 'totalStats', 'meanSecondsBetweenStateMessageEmittedandCommitted'], 'integer') }} as ean_seconds_between_state_message_emit_and_commit,
        {{ json_extract_text_custom('failure_summary', ['failures']) }} as failure_reasons,
        {{ json_extract_text_custom('failure_summary', ['failures', 'failureType']) }} as failure_type,
        {{ json_extract_text_custom('failure_summary', ['failures', 'failureOrigin']) }} as failure_origin,
        {{ json_extract_text_custom('failure_summary', ['failures', 'internalMessage']) }} as internal_message,
        {{ json_extract_text_custom('failure_summary', ['failures', 'externalMessage']) }} as external_message,

        -- Date
        cast(created_at as {{ dbt_utils.type_timestamp() }}) as created_at,
        cast(ended_at as {{ dbt_utils.type_timestamp() }}) as ended_at,
        cast(updated_at as {{ dbt_utils.type_timestamp() }}) as updated_at,
        cast(created_at as {{ dbt_utils.type_timestamp() }}) as loaded_at, 
        date(updated_at) as dt

    from source
)

select * from renamed
