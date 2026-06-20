with all_jobs as (
    select source_job_id, snapshot_date, categories
    from {{ ref('stg_himalayas_jobs') }}

    union all

    select source_job_id, snapshot_date, categories
    from {{ ref('stg_remoteok_jobs') }}
),

exploded as (
    select distinct
        j.source_job_id,
        j.snapshot_date,
        trim(cat.value) as category
    from all_jobs j
    cross join lateral jsonb_array_elements_text(
        case
            when jsonb_typeof(j.categories) = 'array' then j.categories
            else '[]'::jsonb
        end
    ) as cat(value)
)

select source_job_id, snapshot_date, category
from exploded
where category is not null and category <> ''