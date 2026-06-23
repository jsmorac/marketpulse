"""Top-level Dagster Definitions object."""

from dagster import Definitions

from orchestration.assets.ingestion.himalayas_asset import himalayas_raw_jobs
from orchestration.assets.ingestion.remoteok_asset import remoteok_raw_jobs
from orchestration.schedules import daily_ingestion_schedule

defs = Definitions(
    assets=[himalayas_raw_jobs, remoteok_raw_jobs],
    schedules=[daily_ingestion_schedule],
)