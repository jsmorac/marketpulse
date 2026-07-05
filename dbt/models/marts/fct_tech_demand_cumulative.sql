select
    technology,
    tech_group,
    kind,
    count(distinct job_key) as job_count,
    min(snapshot_date) as first_seen,
    max(snapshot_date) as last_seen
from {{ ref('int_job_technologies') }}
group by technology, tech_group, kind
order by job_count desc