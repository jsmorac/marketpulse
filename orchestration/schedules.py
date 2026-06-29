"""Dagster schedules — daily full pipeline (ingest + transform)."""

from dagster import AssetSelection, DefaultScheduleStatus, ScheduleDefinition

daily_pipeline_schedule = ScheduleDefinition(
    name="daily_pipeline",
    cron_schedule="0 6 * * *",
    target=AssetSelection.all(),
    default_status=DefaultScheduleStatus.RUNNING,
)
