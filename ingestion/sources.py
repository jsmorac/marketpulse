"""Registry of the job-board data sources used by MarketPulse.

All four sources require attribution with a direct link, so each one
carries its homepage and a helper to render the attribution string that
must appear in the dashboard footer and the README.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    """A single upstream job-board data source."""

    name: str
    homepage: str
    attribution_required: bool = True


SOURCES: dict[str, Source] = {
    "himalayas": Source("Himalayas", "https://himalayas.app"),
    "remoteok": Source("RemoteOK", "https://remoteok.com"),
    "remotive": Source("Remotive", "https://remotive.com"),
    "hackernews": Source("Hacker News Who is Hiring", "https://news.ycombinator.com"),
}


def attribution_line(source_key: str) -> str:
    """Return the attribution text required by a source's terms of use."""
    source = SOURCES[source_key]
    return f"Data from {source.name} ({source.homepage})"
