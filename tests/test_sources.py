"""Tests for the data-source registry."""

from ingestion.sources import SOURCES, attribution_line


def test_all_four_sources_present():
    assert set(SOURCES) == {"himalayas", "remoteok", "remotive", "hackernews"}


def test_every_source_has_a_homepage():
    assert all(s.homepage.startswith("https://") for s in SOURCES.values())


def test_attribution_line_format():
    assert attribution_line("himalayas") == "Data from Himalayas (https://himalayas.app)"
