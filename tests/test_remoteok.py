from datetime import datetime

from ingestion.remoteok import RemoteOKJob

# Fixture real de la API (copiado del JSON que viste)
CHAOSTRACK_JOB = {
    "slug": "remote-executive-assistant-chaostrack-1133683",
    "id": "1133683",
    "epoch": 1781813310,
    "date": "2026-06-18T20:08:30+00:00",
    "company": "ChaosTrack",
    "company_logo": "",
    "position": "Executive Assistant",
    "tags": ["data entry", "virtual assistant", "customer support", "non tech", "exec"],
    "description": "Posted 12:10:07 PM. Executive Assistant...",
    "location": "",
    "apply_url": "https://remoteOK.com/remote-jobs/remote-executive-assistant-chaostrack-1133683",
    "salary_min": 0,
    "salary_max": 0,
    "logo": "",
    "url": "https://remoteOK.com/remote-jobs/remote-executive-assistant-chaostrack-1133683",
}

RECSEEKERS_JOB = {
    "slug": "remote-operations-administrator-recseekers-1133675",
    "id": "1133675",
    "epoch": 1781809500,
    "date": "2026-06-18T19:05:00+00:00",
    "company": "RECSEEKERS",
    "company_logo": "",
    "position": "Operations Administrator",
    "tags": ["hr", "blockchain", "python", "aws", "dev"],
    "description": "EDTECH OPERATIONS ADMINISTRATOR...",
    "location": "",
    "apply_url": "https://remoteOK.com/remote-jobs/remote-operations-administrator-recseekers-1133675",
    "salary_min": 75000,
    "salary_max": 110000,
    "logo": "",
    "url": "https://remoteOK.com/remote-jobs/remote-operations-administrator-recseekers-1133675",
}


def test_mapeo_campos_basicos():
    """El alias 'id' mapea a guid y 'position' a position correctamente."""
    job = RemoteOKJob.model_validate(CHAOSTRACK_JOB)
    assert job.guid == "1133683"
    assert job.position == "Executive Assistant"
    assert job.company == "ChaosTrack"


def test_tags_preservados():
    """Los tags vienen como lista de strings y se preservan tal cual."""
    job = RemoteOKJob.model_validate(CHAOSTRACK_JOB)
    assert "data entry" in job.tags
    assert "virtual assistant" in job.tags


def test_salary_cero_a_none():
    """salary_min y salary_max en 0 se convierten a None."""
    job = RemoteOKJob.model_validate(CHAOSTRACK_JOB)
    assert job.salary_min is None
    assert job.salary_max is None


def test_salary_real_preservado():
    """Salarios reales (no cero) se preservan como float."""
    job = RemoteOKJob.model_validate(RECSEEKERS_JOB)
    assert job.salary_min == 75000.0
    assert job.salary_max == 110000.0


def test_fecha_con_timezone():
    """La fecha se parsea como datetime con timezone UTC."""
    job = RemoteOKJob.model_validate(CHAOSTRACK_JOB)
    assert isinstance(job.date, datetime)
    assert job.date.tzinfo is not None


def test_tags_vacios_por_defecto():
    """Un job sin tags no falla — devuelve lista vacía."""
    job_sin_tags = {**CHAOSTRACK_JOB, "tags": []}
    job = RemoteOKJob.model_validate(job_sin_tags)
    assert job.tags == []
