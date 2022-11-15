with source as (
    select *
    from {{ source('airbyte_local_db', 'jobs') }}
),

renamed as (
    select
        cast(id as {{ dbt_utils.type_int() }}) as job_id,
        cast(scope as uuid) as connection_id,

        --Unnest config column:,
        status,
        config_type,
        {{ json_extract_text_custom('config', ['sync', 'namespaceDefinition']) }} as namespace_definition,
        {{ json_extract_text_custom('config',['sync', 'namespaceFormat']) }} as namespace_format,
        {{ json_extract_text_custom('config' ,['sync', 'prefix']) }} as prefix,

        {{ json_extract_text_custom('config', ['sync', 'sourceConfiguration']) }} as source_configuration,
        {{ json_extract_text_custom('config', ['sync', 'destinationConfiguration']) }} as destination_configuration,

        {{ json_extract_text_custom('config', ['sync', 'configuredAirbyteCatalog']) }} as configured_airbyte_catalog,
        {{ json_extract_text_custom('config', ['sync', 'sourceDockerImage']) }} as source_docker_image,

        {{ json_extract_text_custom('config', ['sync', 'destinationDockerImage']) }} as destination_docker_image,
        -- json_array_elements(json_extract_path(config::json, 'sync', 'operationSequence')) as operation_sequence,
        {{ json_extract_text_custom('config', ['sync', 'state']) }} as state,
        {{ json_extract_text_custom('config', ['sync', 'resourceRequirements']) }} as resource_requirements,
        {{ json_extract_text_custom('config', ['sync', 'resourceRequirements', 'cpu_request']) }} as cpu_request,
        {{ json_extract_text_custom('config', ['sync', 'resourceRequirements', 'memory_request']) }} as memory_request,

        -- date
        cast(created_at as {{ dbt_utils.type_timestamp() }}) as created_at,
        cast(updated_at as {{ dbt_utils.type_timestamp() }}) as updated_at,
        date(updated_at) as dt
    from source
)

select * from renamed
