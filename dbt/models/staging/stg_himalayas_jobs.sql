with source as (
    select * from raw.himalayas_jobs
),

renamed as (
    select
        source_job_id,
        snapshot_date,
        loaded_at,
        payload->>'title'            as title,
        payload->>'company_name'     as company_name,
        payload->>'company_slug'     as company_slug,
        payload->>'employment_type'  as employment_type,
        payload->>'salary_period'    as salary_period,
        (payload->>'min_salary')::numeric  as min_salary,
        (payload->>'max_salary')::numeric  as max_salary,
        payload->>'currency'         as currency,
        payload->'categories'        as categories,
        payload->'seniority'         as seniority,
        payload->'location_restrictions' as location_restrictions,
        payload->>'excerpt'          as excerpt,
        payload->>'application_link' as application_link,
        (payload->>'pub_date')::timestamptz as pub_date
    from source
)

select * from renamed