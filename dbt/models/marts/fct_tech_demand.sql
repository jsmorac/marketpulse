with job_categories as (
    select
        source_job_id,
        snapshot_date,
        -- normaliza: minúsculas, mapea techs con símbolos, separadores -> un espacio, y rodea con espacios
        ' ' || regexp_replace(
            replace(replace(lower(category), 'c#', 'csharp'), 'c++', 'cplusplus'),
            '[^a-z0-9]+', ' ', 'g'
        ) || ' ' as category_norm
    from {{ ref('int_job_categories') }}
),

tech_aliases as (
    select
        technology,
        tech_group,
        ' ' || regexp_replace(
            replace(replace(lower(alias), 'c#', 'csharp'), 'c++', 'cplusplus'),
            '[^a-z0-9]+', ' ', 'g'
        ) || ' ' as alias_norm
    from {{ ref('known_technologies') }}
),

-- un job cuenta para una tecnología si ALGUNA de sus categorías contiene un alias como palabra completa
job_tech as (
    select distinct
        jc.snapshot_date,
        jc.source_job_id,
        ta.technology,
        ta.tech_group
    from job_categories jc
    inner join tech_aliases ta
        on jc.category_norm like '%' || ta.alias_norm || '%'
),

-- jobs que no hicieron match con ninguna tecnología -> 'other' (a nivel de job, sin solaparse)
all_jobs as (
    select distinct snapshot_date, source_job_id
    from job_categories
),

unmatched as (
    select
        aj.snapshot_date,
        aj.source_job_id,
        'other' as technology,
        'other' as tech_group
    from all_jobs aj
    left join job_tech jt
        on aj.source_job_id = jt.source_job_id
       and aj.snapshot_date = jt.snapshot_date
    where jt.source_job_id is null
),

combined as (
    select * from job_tech
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