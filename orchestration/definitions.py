"""Top-level Dagster Definitions object."""

from dagster import Definitions

from orchestration.assets.ingestion.hackernews_asset import hackernews_raw_jobs
from orchestration.assets.ingestion.himalayas_asset import himalayas_raw_jobs
from orchestration.assets.ingestion.remoteok_asset import remoteok_raw_jobs
from orchestration.assets.transform.dbt_build_asset import dbt_build
from orchestration.schedules import daily_pipeline_schedule, monthly_hackernews_schedule

defs = Definitions(
    assets=[himalayas_raw_jobs, remoteok_raw_jobs, hackernews_raw_jobs, dbt_build],
    schedules=[daily_pipeline_schedule, monthly_hackernews_schedule],
)
