with stargazer as (
    select *
    from {{ source('postgres', 'stargazers') }}
),
users as (
    select *
    from {{ source('postgres', 'stargazers_user') }}
)

SELECT s.repository , s.starred_at, su.login as user_login
FROM stargazers s left outer join stargazers_user su on s.user_id = su.id 
