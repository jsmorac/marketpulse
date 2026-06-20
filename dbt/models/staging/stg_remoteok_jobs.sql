with source as (
    select * from raw.remoteok_jobs
),

renamed as (
    select
        source_job_id,
        snapshot_date,
        loaded_at,
        payload->>'position'     as title,
        payload->>'company'      as company_name,
        payload->>'slug'         as company_slug,
        payload->'tags'          as categories,
        (payload->>'salary_min')::numeric as min_salary,
        (payload->>'salary_max')::numeric as max_salary,
        payload->>'location'     as location,
        payload->>'url'          as application_link,
        (payload->>'date')::timestamptz as pub_date
    from source
)

select * from renamed