from datetime import UTC, datetime

from ingestion.hackernews import HNJob

# Fixtures reales del hilo "Who is hiring? (June 2026)", en la forma cruda de Algolia
ADACORE_CREATED_AT_I = int(datetime(2026, 6, 1, 15, 1, 21, tzinfo=UTC).timestamp())
SMARTERDX_CREATED_AT_I = int(datetime(2026, 6, 1, 15, 1, 33, tzinfo=UTC).timestamp())

ADACORE_JOB = {
    "id": 48357732,
    "author": "glacambre",
    "text": (
        "Adacore | Software Engineers | Full-time | Remote or On-Site"
        "<p>Adacore is the maintainer of GNAT, GCC&#x27;s Ada frontend..."
    ),
    "points": None,
    "story_id": 48357725,
    "parent_id": 48357725,
    "created_at_i": ADACORE_CREATED_AT_I,
}

SMARTERDX_JOB = {
    "id": 48357734,
    "author": "justin_sdx",
    "text": (
        "SmarterDx | 150-250k+ + equity + benefits | Remote (US only) | Multiple roles | "
        '<a href="https://smarterdx.com/careers" rel="nofollow">https://smarterdx.com/careers</a>'
        "<p>SmarterDx builds clinical AI for one of healthcare's most broken systems..."
    ),
    "points": None,
    "story_id": 48357725,
    "parent_id": 48357725,
    "created_at_i": SMARTERDX_CREATED_AT_I,
}


def test_mapeo_campos_basicos():
    """El alias 'id' mapea a guid y los campos básicos se preservan."""
    job = HNJob.from_api(ADACORE_JOB)
    assert job.guid == "48357732"
    assert job.author == "glacambre"
    assert job.story_id == 48357725


def test_guid_convertido_a_string():
    """HN entrega ids como enteros; el modelo los coerciona a string (contrato del loader)."""
    job = HNJob.from_api(ADACORE_JOB)
    assert isinstance(job.guid, str)
    assert job.guid == "48357732"


def test_timestamp_convertido_a_datetime():
    """created_at_i (epoch Unix) se convierte a datetime con timezone UTC."""
    job = HNJob.from_api(ADACORE_JOB)
    assert isinstance(job.created_at, datetime)
    assert job.created_at.tzinfo is not None
    assert job.created_at.year == 2026
    assert job.created_at.month == 6
    assert job.created_at.day == 1


def test_texto_html_preservado():
    """El texto crudo del comentario, con etiquetas HTML, se preserva tal cual."""
    job = HNJob.from_api(SMARTERDX_JOB)
    assert "SmarterDx" in job.text
    assert "<a href=" in job.text


def test_points_null_permitido():
    """points en null (comentarios de HN no siempre lo traen) no rompe el parseo."""
    job = HNJob.from_api(ADACORE_JOB)
    assert job.points is None


def test_parent_id_presente():
    """parent_id apunta al hilo padre — útil para trazabilidad, no para idempotencia."""
    job = HNJob.from_api(SMARTERDX_JOB)
    assert job.parent_id == 48357725