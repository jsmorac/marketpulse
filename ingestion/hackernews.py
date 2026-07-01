"""Client for Hacker News 'Who is hiring?' monthly threads (via the Algolia HN API).

Docs / attribution: https://news.ycombinator.com  (thread comments are the job posts)
Rate limit: Algolia is generous — tenacity retries cover transient errors.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field, field_validator
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

HN_ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"
HN_ALGOLIA_ITEM_URL = "https://hn.algolia.com/api/v1/items/{thread_id}"
HACKERNEWS_SOURCE = "hackernews"
HACKERNEWS_ATTRIBUTION = "https://news.ycombinator.com"
HEADERS = {"User-Agent": "marketpulse-portfolio/1.0 (github.com/jsmorac/marketpulse)"}


class HNJob(BaseModel):
    """A single top-level comment (one job posting) from an HN 'Who is hiring?' thread."""

    guid: str = Field(alias="id")
    author: str | None = None
    text: str
    points: int | None = None
    story_id: int | None = None
    parent_id: int | None = None
    created_at: datetime = Field(alias="created_at_i")

    model_config = {"populate_by_name": True}

    @field_validator("guid", mode="before")
    @classmethod
    def id_to_str(cls, v: Any) -> str:
        """HN comment ids arrive as ints; the loader's guid contract is str."""
        return str(v)

    @classmethod
    def from_api(cls, data: dict) -> HNJob:
        """Build an HNJob from a raw Algolia comment dict, converting the Unix timestamp."""
        data = data.copy()
        data["created_at_i"] = datetime.fromtimestamp(data["created_at_i"], tz=UTC)
        return cls.model_validate(data, by_alias=True)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def find_latest_thread() -> str:
    """Return the objectID of the most recent 'Who is hiring?' thread.

    The `whoishiring` bot posts three monthly threads (hiring, wants-to-be-hired,
    freelancer). We filter by title to make sure we grab the hiring one, not a sibling.
    """
    params = {"tags": "story,author_whoishiring", "query": "Who is Hiring"}
    with httpx.Client(timeout=30) as client:
        response = client.get(HN_ALGOLIA_SEARCH_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        hits = response.json()["hits"]

    for hit in hits:
        if "who is hiring" in (hit.get("title") or "").lower():
            logger.info("Latest HN hiring thread: %s (%s)", hit["objectID"], hit.get("title"))
            return str(hit["objectID"])

    raise ValueError("No 'Who is hiring?' thread found in Algolia results")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def fetch_jobs(thread_id: str | None = None) -> list[HNJob]:
    """Fetch all top-level job comments from the current month's HN hiring thread.

    If `thread_id` is None, the latest thread is discovered automatically.
    Nested replies are ignored — only top-level comments are jobs. The whole thread
    arrives in a single request (no pagination). Deleted/empty comments are skipped.
    """
    if thread_id is None:
        thread_id = find_latest_thread()

    url = HN_ALGOLIA_ITEM_URL.format(thread_id=thread_id)
    with httpx.Client(timeout=30) as client:
        response = client.get(url, headers=HEADERS)
        response.raise_for_status()
        thread = response.json()

    jobs = []
    for comment in thread.get("children", []):
        if not comment.get("text"):
            continue  # deleted or empty comment
        try:
            jobs.append(HNJob.from_api(comment))
        except Exception:
            logger.warning("Skipping invalid HN comment: %s", comment.get("id"))
            continue

    logger.info("Fetched %d job comments from HN thread %s", len(jobs), thread_id)
    return jobs
