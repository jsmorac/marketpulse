with hn_jobs as (
    select
        source || ':' || source_job_id as job_key,
        snapshot_date,
        {{ normalize_for_tech_match("regexp_replace(body_html, '<[^>]+>', ' ', 'g')") }} as text_norm
    from {{ ref('stg_hackernews_jobs') }}
),
tech_aliases as (
    select
        technology,
        tech_group,
        {{ normalize_for_tech_match('alias') }} as alias_norm
    from {{ ref('known_technologies') }}
)
select distinct
    hj.snapshot_date,
    hj.job_key,
    ta.technology,
    ta.tech_group
from hn_jobs hj
inner join tech_aliases ta
    on hj.text_norm like '%' || ta.alias_norm || '%'