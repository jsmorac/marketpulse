from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any, Protocol
from uuid import uuid4

from psycopg import Connection
from psycopg.types.json import Jsonb

from db.connection import connect


class LoadableJob(Protocol):
    """Cualquier job que el loader pueda procesar.

    Solo exige un campo: guid (el ID único en la fuente).
    El resto va al payload como JSON.
    """

    guid: str | int


def _upsert_sql(table: str) -> str:
    return f"""
INSERT INTO raw.{table}
    (source, source_job_id, snapshot_date, run_id, payload, loaded_at)
VALUES
    (%(source)s, %(source_job_id)s, %(snapshot_date)s, %(run_id)s, %(payload)s, now())
ON CONFLICT (source_job_id, snapshot_date) DO UPDATE SET
    payload   = EXCLUDED.payload,
    run_id    = EXCLUDED.run_id,
    loaded_at = now()
RETURNING (xmax = 0) AS inserted;
"""


@dataclass(frozen=True)
class LoadResult:
    inserted: int
    updated: int
    snapshot_date: date
    run_id: str

    @property
    def total(self) -> int:
        return self.inserted + self.updated


def job_to_row(
    job: LoadableJob,
    source: str,
    snapshot_date: date,
    run_id: str,
) -> dict[str, Any]:
    """Función PURA: job -> fila. Sin BD, fácil de testear."""
    return {
        "source": source,
        "source_job_id": str(job.guid),
        "snapshot_date": snapshot_date,
        "run_id": run_id,
        "payload": job.model_dump(mode="json"),
    }


def load_jobs(
    jobs: Sequence[LoadableJob],
    *,
    source: str,
    table: str,
    snapshot_date: date | None = None,
    run_id: str | None = None,
    conn: Connection | None = None,
) -> LoadResult:
    snapshot_date = snapshot_date or datetime.now(UTC).date()
    run_id = run_id or str(uuid4())

    rows = [job_to_row(j, source, snapshot_date, run_id) for j in jobs]
    if not rows:
        return LoadResult(0, 0, snapshot_date, run_id)

    params = [{**r, "payload": Jsonb(r["payload"])} for r in rows]
    sql = _upsert_sql(table)

    own_conn = conn is None
    conn = conn or connect()
    try:
        inserted = updated = 0
        with conn.cursor() as cur:
            cur.executemany(sql, params, returning=True)
            while True:
                rec = cur.fetchone()
                if rec is not None:
                    if rec[0]:
                        inserted += 1
                    else:
                        updated += 1
                if not cur.nextset():
                    break
        if own_conn:
            conn.commit()
        return LoadResult(inserted, updated, snapshot_date, run_id)
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()
