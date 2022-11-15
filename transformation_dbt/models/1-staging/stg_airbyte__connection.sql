with source as (
    select *
    from {{ source('airbyte_local_db', 'connection') }}
),

renamed as (
    select
        id as connection_id,
        name,
        manual,
        prefix,
        status,
        catalog,
        schedule,
        source_id,
        destination_id,
        namespace_format,
        namespace_definition,

        resource_requirements,

        {{ json_extract_text_custom('schedule', 'timeUnit') }} as time_unit,
        {{ json_extract_text_custom('schedule', 'units', 'integer') }} as units

    from source
)

select * from renamed
