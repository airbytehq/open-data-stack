with source as (
    select *
    from {{ source('airbyte_local_db', 'actor_definition') }}
),

renamed as (
    select
        id as connector_definition_id,
        icon,
        name as connector_name,
        spec,
        actor_type as connector_type,

        source_type as connector_category,
        docker_image_tag,
        docker_repository,
        documentation_url,

        tombstone,
        release_date,
        release_stage,
        resource_requirements
    from source
)

select * from renamed
