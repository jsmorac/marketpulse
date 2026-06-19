with staging as (
    select
        source_job_id,
        snapshot_date,
        categories
    from {{ ref('stg_himalayas_jobs') }}
),

exploded as (
    select distinct
        s.source_job_id,
        s.snapshot_date,
        trim(cat.value) as category
    from staging s
    cross join lateral jsonb_array_elements_text(
        case
            when jsonb_typeof(s.categories) = 'array' then s.categories
            else '[]'::jsonb
        end
    ) as cat(value)
)

select source_job_id, snapshot_date, category
from exploded
where category is not null and category <> ''