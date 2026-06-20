# tests/test_loader.py
from datetime import date

from ingestion.loader import LoadResult, job_to_row, load_jobs


class FakeJob:
    """job_to_row solo necesita .guid y .model_dump(mode='json')."""

    def __init__(self, guid, payload):
        self.guid = guid
        self._payload = payload

    def model_dump(self, *, mode="python"):
        return dict(self._payload)


def test_job_to_row_mapea_campos_fijos():
    job = FakeJob(guid="abc-123", payload={"title": "Data Engineer"})
    row = job_to_row(job, source="himalayas", snapshot_date=date(2026, 1, 1), run_id="run-1")
    assert row["source"] == "himalayas"
    assert row["source_job_id"] == "abc-123"
    assert row["snapshot_date"] == date(2026, 1, 1)
    assert row["run_id"] == "run-1"
    assert row["payload"] == {"title": "Data Engineer"}


def test_job_to_row_usa_el_modelo_real(sample_jobs):
    """Sin BD: valida que el atributo de id del modelo real es el correcto."""
    job = sample_jobs[0]
    row = job_to_row(job, source="himalayas", snapshot_date=date(2026, 1, 1), run_id="run-1")
    assert row["source_job_id"] == str(job.guid)
    assert row["payload"] == job.model_dump(mode="json")


def test_load_vacio_no_toca_la_bd():
    res = load_jobs(
        [],
        source="himalayas",
        table="himalayas_jobs",
        snapshot_date=date(2026, 1, 1),
        run_id="run-1",
    )
    assert res == LoadResult(0, 0, date(2026, 1, 1), "run-1")


def test_upsert_es_idempotente(db_conn, sample_jobs):
    snap = date(2026, 1, 1)
    db_conn.execute("delete from raw.himalayas_jobs where snapshot_date = %s", [snap])

    r1 = load_jobs(
        sample_jobs,
        source="himalayas",
        table="himalayas_jobs",
        snapshot_date=snap,
        run_id="run-1",
        conn=db_conn,
    )
    assert (r1.inserted, r1.updated) == (2, 0)

    r2 = load_jobs(
        sample_jobs,
        source="himalayas",
        table="himalayas_jobs",
        snapshot_date=snap,
        run_id="run-2",
        conn=db_conn,
    )
    assert (r2.inserted, r2.updated) == (0, 2)

    count = db_conn.execute(
        "select count(*) from raw.himalayas_jobs where snapshot_date = %s", [snap]
    ).fetchone()[0]
    assert count == 2
