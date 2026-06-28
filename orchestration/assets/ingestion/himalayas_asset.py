"""Ingestion assets: one asset per upstream source."""

from dagster import asset

from ingestion.himalayas import fetch_all_jobs
from ingestion.loader import load_jobs


@asset(group_name="ingestion")
def himalayas_raw_jobs() -> None:
    """Fetch all Himalayas jobs and load into raw.himalayas_jobs."""
    jobs = fetch_all_jobs()
    total = len(jobs)
    result = load_jobs(jobs, source="himalayas", table="himalayas_jobs")
    print(
        f"Himalayas: {total} total jobs en la API. "
        f"{result.inserted} insertados, {result.updated} actualizados."
    )
