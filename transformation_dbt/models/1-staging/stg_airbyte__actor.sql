with source as (
    select *
    from {{ source('airbyte_local_db', 'actor') }}
),

renamed as (
    select
        id as connector_id,
        name as connector_name,
        tombstone,
        actor_type as connector_type,
        workspace_id,
        configuration,
        actor_definition_id as connector_definition_id

    from source
)

select * from renamed
