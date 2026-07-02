"""Dagster schedules — daily pipeline (ingest + transform) plus HN's monthly cadence.

HackerNews is excluded from the daily pipeline: unlike Himalayas/RemoteOK (live boards
that genuinely change day to day), the HN 'Who is hiring?' thread is a static set of
comments that barely grows after its first few days. Re-ingesting it daily just recounted
the same ~300 jobs over and over under a new snapshot_date, inflating demand numbers
with no new signal. It gets its own monthly schedule instead — see seguimiento.md
for the full diagnosis (2026-07-02).
"""

from dagster import AssetSelection, DefaultScheduleStatus, ScheduleDefinition

daily_pipeline_schedule = ScheduleDefinition(
    name="daily_pipeline",
    cron_schedule="0 6 * * *",
    target=AssetSelection.all() - AssetSelection.assets("hackernews_raw_jobs"),
    default_status=DefaultScheduleStatus.RUNNING,
)

monthly_hackernews_schedule = ScheduleDefinition(
    name="monthly_hackernews",
    cron_schedule="0 6 3 * *",  # día 3 de cada mes — deja que se asiente la ráfaga inicial
    target=AssetSelection.assets("hackernews_raw_jobs") | AssetSelection.assets("dbt_build"),
    default_status=DefaultScheduleStatus.RUNNING,
)
