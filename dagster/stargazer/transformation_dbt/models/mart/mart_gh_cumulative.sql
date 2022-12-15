


with stargazer as (
    select *
    from {{ source('postgres', 'stargazers') }}
),
users as (
    select *
    from {{ source('postgres', 'stargazers_user') }}
),


per_month as (
SELECT repository , to_char(s.starred_at , 'YYYY-MM') as starred_at_month, count(*) as sum_stars
FROM stargazers  s left outer join users su on s.user_id = su.id 
group by repository,to_char(s.starred_at , 'YYYY-MM')
)

SELECT repository, starred_at_month, sum_stars
, sum(s.sum_stars) over (partition by repository order by starred_at_month) as cumulative_stargazers

FROM per_month s
group by repository, starred_at_month, sum_stars
order by repository, starred_at_month
