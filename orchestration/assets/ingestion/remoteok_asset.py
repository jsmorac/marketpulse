"""Ingestion asset for RemoteOK."""

from dagster import asset

from ingestion.loader import load_jobs
from ingestion.remoteok import fetch_jobs


@asset(group_name="ingestion")
def remoteok_raw_jobs() -> None:
    """Fetch jobs from RemoteOK and load into raw.remoteok_jobs."""
    jobs = fetch_jobs()
    result = load_jobs(jobs, source="remoteok", table="remoteok_jobs")
    print(f"RemoteOK: {result.inserted} insertados, {result.updated} actualizados.")
