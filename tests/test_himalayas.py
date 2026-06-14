"""Tests for the Himalayas API client."""

from datetime import UTC, datetime

from ingestion.himalayas import HimalayasJob

# JSON real de la API — copiado de la respuesta que trajiste antes
MERCOR_JOB = {
    "title": "Feedback Synthesis Specialist - Remote | Upto $120/hr",
    "excerpt": "Mercor connects elite talent with AI research labs.",
    "companyName": "mercor",
    "companySlug": "mercor",
    "companyLogo": "https://cdn-images.himalayas.app/6jo5q9nua35jgtdfm41nq6b7ocqf",
    "employmentType": "Contractor",
    "minSalary": 80,
    "maxSalary": 120,
    "salaryPeriod": "hourly",
    "seniority": ["Mid-level"],
    "currency": "USD",
    "locationRestrictions": ["India"],
    "timezoneRestrictions": [5.5],
    "categories": ["Feedback-Specialist", "AI-Quality-Assurance"],
    "parentCategories": [],
    "description": "<h3>About the job</h3>",
    "pubDate": 1781459499,
    "expiryDate": 1786643498,
    "applicationLink": "https://himalayas.app/companies/mercor/jobs/feedback-synthesis-specialist",
    "guid": "https://himalayas.app/companies/mercor/jobs/feedback-synthesis-specialist",
}

GENESIS_JOB = {
    "title": "Strong Junior Manual QA Engineer",
    "excerpt": "We are looking for a Strong Junior Manual QA Engineer.",
    "companyName": "Genesis",
    "companySlug": "genesis",
    "companyLogo": "https://cdn-images.himalayas.app/pc9ii6di0lpbsvixmoaq9v22pckv",
    "employmentType": "Full Time",
    "minSalary": None,
    "maxSalary": None,
    "salaryPeriod": "annual",
    "seniority": ["Entry-level"],
    "currency": None,
    "locationRestrictions": ["Poland", "Ukraine"],
    "timezoneRestrictions": [1, 2, 3],
    "categories": ["Manual-QA-Engineer", "QA-Engineer"],
    "parentCategories": ["Developer"],
    "description": "<div>Hello.</div>",
    "pubDate": 1781459465,
    "expiryDate": 1786643464,
    "applicationLink": "https://himalayas.app/companies/genesis/jobs/strong-junior-manual-qa-engineer",
    "guid": "https://himalayas.app/companies/genesis/jobs/strong-junior-manual-qa-engineer",
}


def test_camel_case_fields_map_to_snake_case():
    """Los campos camelCase de la API se mapean correctamente a snake_case en el modelo."""
    job = HimalayasJob.from_api(MERCOR_JOB)
    assert job.company_name == "mercor"
    assert job.company_slug == "mercor"
    assert job.employment_type == "Contractor"


def test_job_without_salary_is_accepted():
    """Un trabajo con salario y moneda nulos se acepta sin reventar (caso mayoritario en la API)."""
    job = HimalayasJob.from_api(GENESIS_JOB)
    assert job.min_salary is None
    assert job.max_salary is None
    assert job.currency is None


def test_pub_date_is_converted_from_timestamp():
    """El timestamp Unix de pubDate se convierte a un datetime real con zona horaria UTC."""
    job = HimalayasJob.from_api(MERCOR_JOB)
    assert isinstance(job.pub_date, datetime)
    assert job.pub_date.tzinfo == UTC
    assert job.pub_date.year == 2026


def test_list_fields_are_preserved():
    """Las listas (seniority, ubicaciones, zonas horarias) llegan intactas."""
    job = HimalayasJob.from_api(MERCOR_JOB)
    assert job.seniority == ["Mid-level"]
    assert job.location_restrictions == ["India"]
    assert job.timezone_restrictions == [5.5]


def test_integer_timezones_are_coerced_to_float():
    """La API a veces manda zonas como enteros (1,2,3) y otras como 5.5 — todo debe quedar float."""
    job = HimalayasJob.from_api(GENESIS_JOB)
    assert job.timezone_restrictions == [1.0, 2.0, 3.0]


def test_job_without_expiry_date_is_accepted():
    """Un trabajo sin fecha de expiración no debe reventar."""
    job_data = {k: v for k, v in MERCOR_JOB.items() if k != "expiryDate"}
    job = HimalayasJob.from_api(job_data)
    assert job.expiry_date is None
