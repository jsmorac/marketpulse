"""Client for the Himalayas public jobs API.

Docs / attribution: https://himalayas.app/api
Rate limit: unknown — use tenacity retries on 429.
"""

from datetime import UTC, datetime

import httpx
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

BASE_URL = "https://himalayas.app/jobs/api"
DEFAULT_LIMIT = 100


class HimalayasJob(BaseModel):
    """A single job posting as returned by the Himalayas API."""

    guid: str
    title: str
    company_name: str = Field(alias="companyName")
    company_slug: str = Field(alias="companySlug")
    company_logo: str | None = Field(alias="companyLogo", default=None)
    employment_type: str | None = Field(alias="employmentType", default=None)
    seniority: list[str] = Field(default_factory=list)
    min_salary: float | None = Field(alias="minSalary", default=None)
    max_salary: float | None = Field(alias="maxSalary", default=None)
    salary_period: str | None = Field(alias="salaryPeriod", default=None)
    currency: str | None = None
    categories: list[str] = Field(default_factory=list)
    parent_categories: list[str] = Field(alias="parentCategories", default_factory=list)
    location_restrictions: list[str] = Field(alias="locationRestrictions", default_factory=list)
    timezone_restrictions: list[float] = Field(alias="timezoneRestrictions", default_factory=list)
    excerpt: str | None = None
    description_html: str | None = Field(alias="description", default=None)
    application_link: str = Field(alias="applicationLink")
    pub_date: datetime = Field(alias="pubDate")
    expiry_date: datetime | None = Field(alias="expiryDate", default=None)

    model_config = {"populate_by_name": True}

    @classmethod
    def from_api(cls, data: dict) -> "HimalayasJob":
        """Build a HimalayasJob from a raw API dict, converting timestamps to datetimes."""
        data = data.copy()
        data["pubDate"] = datetime.fromtimestamp(data["pubDate"], tz=UTC)
        if data.get("expiryDate"):
            data["expiryDate"] = datetime.fromtimestamp(data["expiryDate"], tz=UTC)
        return cls.model_validate(data, by_alias=True)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def fetch_jobs(offset: int = 0, limit: int = DEFAULT_LIMIT) -> tuple[list[HimalayasJob], int]:
    """Fetch one page of jobs from Himalayas.

    Returns a tuple of (jobs, total_count).
    Retries up to 3 times with exponential backoff on transient errors.
    """
    params = {"offset": offset, "limit": limit}
    with httpx.Client(timeout=30) as client:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()

    data = response.json()
    jobs = [HimalayasJob.from_api(job) for job in data["jobs"]]
    total_count: int = data["totalCount"]
    return jobs, total_count


def fetch_all_jobs() -> list[HimalayasJob]:
    """Fetch every available job by paginating through the API."""
    all_jobs: list[HimalayasJob] = []

    first_page, total_count = fetch_jobs(offset=0)
    all_jobs.extend(first_page)
    offset = len(first_page)

    while offset < total_count:
        page, _ = fetch_jobs(offset=offset)
        if not page:
            break
        all_jobs.extend(page)
        offset += len(page)

    return all_jobs
