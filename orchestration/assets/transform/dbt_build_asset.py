"""Asset that runs `dbt build` after the raw ingestion assets.

Wraps the dbt CLI as a subprocess so the full pipeline (ingest -> transform)
appears as a single lineage in the Dagster UI.
"""

import subprocess
from pathlib import Path

from dagster import AssetExecutionContext, asset

from orchestration.assets.ingestion.himalayas_asset import himalayas_raw_jobs
from orchestration.assets.ingestion.remoteok_asset import remoteok_raw_jobs

DBT_DIR = Path(__file__).resolve().parents[3] / "dbt"


@asset(
    group_name="transform",
    deps=[himalayas_raw_jobs, remoteok_raw_jobs],
)
def dbt_build(context: AssetExecutionContext) -> None:
    """Run `dbt build` (seed + run + test) against the freshly ingested raw data."""
    result = subprocess.run(
        ["dbt", "build", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        context.log.info(result.stdout)
    if result.stderr:
        context.log.warning(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"dbt build failed (exit code {result.returncode})")
