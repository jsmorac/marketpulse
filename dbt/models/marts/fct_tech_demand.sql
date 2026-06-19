with job_categories as (
    select
        source_job_id,
        snapshot_date,
        category
    from {{ ref('int_himalayas_job_categories') }}
),

tech_lookup as (
    select
        technology,
        keyword,
        tech_group
    from {{ ref('known_technologies') }}
),

matched as (
    select
        jc.snapshot_date,
        kt.technology,
        kt.tech_group,
        jc.source_job_id
    from job_categories jc
    inner join tech_lookup kt
        on jc.category ilike '%' || kt.keyword || '%'
),

unmatched as (
    select
        jc.snapshot_date,
        'other'         as technology,
        'other'         as tech_group,
        jc.source_job_id
    from job_categories jc
    where not exists (
        select 1
        from tech_lookup kt
        where jc.category ilike '%' || kt.keyword || '%'
    )
),

combined as (
    select * from matched
    union all
    select * from unmatched
)

select
    snapshot_date,
    technology,
    tech_group,
    count(distinct source_job_id) as job_count
from combined
group by snapshot_date, technology, tech_group
order by snapshot_date desc, job_count desc