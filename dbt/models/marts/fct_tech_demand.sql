select
    snapshot_date,
    technology,
    tech_group,
    kind,
    count(distinct job_key) as job_count
from {{ ref('int_job_technologies') }}
group by snapshot_date, technology, tech_group, kind
order by snapshot_date desc, job_count desc