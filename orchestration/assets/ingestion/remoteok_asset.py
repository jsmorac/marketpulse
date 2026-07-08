"""Ingestion asset for RemoteOK."""

from dagster import AssetExecutionContext, asset

from ingestion.loader import load_jobs
from ingestion.remoteok import fetch_jobs


@asset(group_name="ingestion")
def remoteok_raw_jobs(context: AssetExecutionContext) -> None:
    """Fetch all jobs from RemoteOK and load into raw.remoteok_jobs."""
    jobs = fetch_jobs(limit=1000)
    result = load_jobs(jobs, source="remoteok", table="remoteok_jobs")
    context.log.info(f"RemoteOK: {result.inserted} insertados, {result.updated} actualizados.")
