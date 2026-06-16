# tests/conftest.py
import pytest
from test_himalayas import GENESIS_JOB, MERCOR_JOB  # tus fixtures crudas ya existentes

from ingestion.himalayas import HimalayasJob


@pytest.fixture
def sample_jobs() -> list[HimalayasJob]:
    return [HimalayasJob.from_api(MERCOR_JOB), HimalayasJob.from_api(GENESIS_JOB)]


@pytest.fixture
def db_conn():
    psycopg = pytest.importorskip("psycopg")
    from db.connection import connect

    try:
        conn = connect()
    except psycopg.OperationalError:
        pytest.skip("Postgres no disponible (¿Docker arriba?)")
    conn.autocommit = False
    try:
        yield conn
    finally:
        conn.rollback()  # deshace todo lo que el test insertó
        conn.close()
