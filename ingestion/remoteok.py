from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field, field_validator
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

REMOTEOK_API_URL = "https://remoteok.com/api"
REMOTEOK_SOURCE = "remoteok"
REMOTEOK_ATTRIBUTION = "https://remoteok.com"


class RemoteOKJob(BaseModel):
    """Un job de la API de RemoteOK."""

    guid: str = Field(alias="id")
    slug: str
    position: str
    company: str
    tags: list[str] = Field(default_factory=list)
    date: datetime
    location: str = ""
    description: str = ""
    apply_url: str = Field(alias="apply_url")
    url: str
    salary_min: float | None = None
    salary_max: float | None = None

    @field_validator("salary_min", "salary_max", mode="before")
    @classmethod
    def zero_to_none(cls, v: Any) -> float | None:
        """RemoteOK manda 0 cuando no hay salario — lo convertimos a None."""
        if v == 0:
            return None
        return v

    model_config = {"populate_by_name": True}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def fetch_jobs(limit: int | None = None) -> list[RemoteOKJob]:
    """Trae los primeros `limit` jobs de RemoteOK.

    El primer objeto del array es metadata legal — lo saltamos.
    Los tags vienen en minúsculas con espacios ('python', 'react').
    """
    headers = {"User-Agent": "marketpulse-portfolio/1.0 (github.com/jsmorac/marketpulse)"}

    with httpx.Client(timeout=30) as client:
        response = client.get(REMOTEOK_API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()

    # El primer elemento es siempre metadata legal, no un job
    jobs_raw = [item for item in data if "id" in item]

    jobs = []
    for raw in jobs_raw[:limit] if limit else jobs_raw:
        try:
            jobs.append(RemoteOKJob.model_validate(raw))
        except Exception:
            logger.warning("Skipping invalid RemoteOK job: %s", raw.get("id"))
            continue

    logger.info("Fetched %d jobs from RemoteOK", len(jobs))
    return jobs
