"""Tests for the fetch step (api): parse RSS/Atom feeds."""

from datetime import datetime
from unittest.mock import patch

import httpx

from content_workflow.fetch import fetch_articles

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Test Blog</title>
    <item>
        <title>First Post</title>
        <link>https://blog.example.com/first</link>
        <description>This is the first post about AI workflows.</description>
        <pubDate>Mon, 01 Jan 2026 12:00:00 GMT</pubDate>
    </item>
    <item>
        <title>Second Post</title>
        <link>https://blog.example.com/second</link>
        <description>A deep dive into automation patterns.</description>
        <pubDate>Tue, 02 Jan 2026 12:00:00 GMT</pubDate>
    </item>
</channel>
</rss>"""

SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Atom Blog</title>
    <entry>
        <title>Atom Entry</title>
        <link href="https://atom.example.com/entry1"/>
        <summary>An atom feed entry about testing.</summary>
        <updated>2026-01-15T10:00:00Z</updated>
    </entry>
</feed>"""


def _mock_response(text: str, url: str = "https://example.com/feed"):
    return httpx.Response(200, text=text, request=httpx.Request("GET", url))


def test_fetch_rss_articles():
    """RSS feed items are parsed into Article objects."""
    with patch("content_workflow.fetch.httpx.get", return_value=_mock_response(SAMPLE_RSS)):
        articles = fetch_articles(["https://example.com/feed"])

    assert len(articles) == 2
    assert articles[0].title == "First Post"
    assert "AI workflows" in articles[0].content
    assert articles[0].url == "https://blog.example.com/first"
    assert isinstance(articles[0].fetched_at, datetime)


def test_fetch_atom_articles():
    """Atom feed entries are parsed into Article objects."""
    with patch("content_workflow.fetch.httpx.get", return_value=_mock_response(SAMPLE_ATOM)):
        articles = fetch_articles(["https://atom.example.com/feed"])

    assert len(articles) == 1
    assert articles[0].title == "Atom Entry"
    assert "testing" in articles[0].content
    assert articles[0].url == "https://atom.example.com/entry1"


def test_fetch_skips_failed_feeds():
    """Failed HTTP requests are skipped without raising errors."""
    mock_response = httpx.Response(404, request=httpx.Request("GET", "https://broken.example.com"))

    with patch("content_workflow.fetch.httpx.get", return_value=mock_response):
        articles = fetch_articles(["https://broken.example.com/feed"])

    assert len(articles) == 0


def test_fetch_limits_articles():
    """Only the most recent N articles are returned per feed."""
    with patch("content_workflow.fetch.httpx.get", return_value=_mock_response(SAMPLE_RSS)):
        articles = fetch_articles(["https://example.com/feed"], max_per_feed=1)

    assert len(articles) == 1
    assert articles[0].title == "First Post"


def test_fetch_multiple_feeds():
    """Articles from multiple feeds are combined."""
    with patch("content_workflow.fetch.httpx.get", side_effect=[
        _mock_response(SAMPLE_RSS),
        _mock_response(SAMPLE_ATOM),
    ]):
        articles = fetch_articles([
            "https://example.com/feed",
            "https://atom.example.com/feed",
        ])

    assert len(articles) == 3


def test_fetch_skips_network_errors():
    """Network errors (timeout, DNS failure) are skipped, not raised."""
    with patch("content_workflow.fetch.httpx.get", side_effect=httpx.ConnectError("Connection refused")):
        articles = fetch_articles(["https://unreachable.example.com/feed"])

    assert len(articles) == 0
