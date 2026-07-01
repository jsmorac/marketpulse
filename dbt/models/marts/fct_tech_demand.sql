with job_categories as (
    select
        source || ':' || source_job_id as job_key,
        snapshot_date,
        {{ normalize_for_tech_match('category') }} as category_norm
    from {{ ref('int_job_categories') }}
),

tech_aliases as (
    select
        technology,
        tech_group,
        {{ normalize_for_tech_match('alias') }} as alias_norm
    from {{ ref('known_technologies') }}
),

category_based_matches as (
    select distinct
        jc.snapshot_date,
        jc.job_key,
        ta.technology,
        ta.tech_group
    from job_categories jc
    inner join tech_aliases ta
        on jc.category_norm like '%' || ta.alias_norm || '%'
),

text_based_matches as (
    select
        snapshot_date,
        job_key,
        technology,
        tech_group
    from {{ ref('int_hackernews_technologies') }}
),

job_tech as (
    select snapshot_date, job_key, technology, tech_group from category_based_matches
    union
    select snapshot_date, job_key, technology, tech_group from text_based_matches
),

all_jobs as (
    select snapshot_date, job_key from job_categories
    union
    select
        snapshot_date,
        source || ':' || source_job_id as job_key
    from {{ ref('stg_hackernews_jobs') }}
),

unmatched as (
    select
        aj.snapshot_date,
        aj.job_key,
        'other' as technology,
        'other' as tech_group
    from all_jobs aj
    left join job_tech jt
        on aj.job_key = jt.job_key
       and aj.snapshot_date = jt.snapshot_date
    where jt.job_key is null
)

select
    snapshot_date,
    technology,
    tech_group,
    count(distinct job_key) as job_count
from (
    select * from job_tech
    union all
    select * from unmatched
) combined
group by snapshot_date, technology, tech_group
order by snapshot_date desc, job_count desc