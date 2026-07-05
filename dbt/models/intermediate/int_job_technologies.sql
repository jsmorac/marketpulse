{{ config(materialized='table') }}

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
        kind,
        {{ normalize_for_tech_match('alias') }} as alias_norm
    from {{ ref('known_technologies') }}
),

category_based_matches as (
    select distinct
        jc.snapshot_date,
        jc.job_key,
        ta.technology,
        ta.tech_group,
        ta.kind
    from job_categories jc
    inner join tech_aliases ta
        on jc.category_norm like '%' || ta.alias_norm || '%'
),

text_based_matches as (
    select snapshot_date, job_key, technology, tech_group, kind
    from {{ ref('int_hackernews_technologies') }}
),

matched as (
    select snapshot_date, job_key, technology, tech_group, kind from category_based_matches
    union
    select snapshot_date, job_key, technology, tech_group, kind from text_based_matches
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
        'other' as tech_group,
        'other' as kind
    from all_jobs aj
    left join matched m
        on aj.job_key = m.job_key
       and aj.snapshot_date = m.snapshot_date
    where m.job_key is null
)

select * from matched
union all
select * from unmatched