with source as (
    select * from raw.hackernews_jobs
),
renamed as (
    select
        source,
        source_job_id,
        snapshot_date,
        loaded_at,
        payload->>'author'     as author,
        payload->>'text'       as body_html,
        (payload->>'created_at')::timestamptz as posted_at,
        (payload->>'story_id')::bigint as story_id
    from source
)
select * from renamed