with source as (
    select *
    from {{ source('airbyte_local_db', 'workspace') }}
),



renamed as (
    select
        id as workspace_id,
        name as workspace_name,
        slug,
        email,
        tombstone,
        customer_id,
        notifications,
        send_newsletter,
        feedback_complete,
        first_sync_complete,
        display_setup_wizard,
        send_security_updates,
        initial_setup_complete,
        anonymous_data_collection

    from source
)

select * from renamed
