"""Ingestion asset for Hacker News 'Who is hiring?' threads."""

from dagster import AssetExecutionContext, asset

from ingestion.hackernews import fetch_jobs
from ingestion.loader import load_jobs


@asset(group_name="ingestion")
def hackernews_raw_jobs(context: AssetExecutionContext) -> None:
    """Fetch the current month's HN 'Who is hiring?' jobs into raw.hackernews_jobs."""
    jobs = fetch_jobs()
    result = load_jobs(jobs, source="hackernews", table="hackernews_jobs")
    context.log.info(f"HackerNews: {result.inserted} insertados, {result.updated} actualizados.")
