"""Dagster schedules — daily ingestion pipeline."""

from dagster import AssetSelection, DefaultScheduleStatus, ScheduleDefinition

from orchestration.assets.ingestion.himalayas_asset import himalayas_raw_jobs

daily_ingestion_schedule = ScheduleDefinition(
    name="daily_himalayas_ingestion",
    cron_schedule="0 6 * * *",
    target=AssetSelection.assets(himalayas_raw_jobs),
    default_status=DefaultScheduleStatus.RUNNING,
)
