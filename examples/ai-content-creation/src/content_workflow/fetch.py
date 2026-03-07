"""Fetch step (api): retrieve articles from RSS/Atom feeds."""

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import httpx

from content_workflow.models import Article

# Atom namespace
_ATOM_NS = "{http://www.w3.org/2005/Atom}"


def fetch_articles(feed_urls: list[str], max_per_feed: int = 5) -> list[Article]:
    """Fetch articles from RSS/Atom feed URLs.

    Args:
        feed_urls: List of RSS or Atom feed URLs.
        max_per_feed: Maximum articles to take from each feed.
    """
    articles = []
    for url in feed_urls:
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
        except httpx.HTTPError:
            continue
        if response.status_code != 200:
            continue
        articles.extend(_parse_feed(response.text, max_per_feed))
    return articles


def _parse_feed(xml_text: str, max_items: int) -> list[Article]:
    """Parse RSS or Atom feed XML into Article objects."""
    root = ET.fromstring(xml_text)

    # Detect feed type
    if root.tag == "rss":
        return _parse_rss(root, max_items)
    if root.tag == f"{_ATOM_NS}feed":
        return _parse_atom(root, max_items)
    return []


def _parse_rss(root: ET.Element, max_items: int) -> list[Article]:
    """Parse RSS 2.0 feed."""
    channel = root.find("channel")
    if channel is None:
        return []

    articles = []
    for item in channel.findall("item")[:max_items]:
        title = _text(item, "title")
        link = _text(item, "link")
        description = _text(item, "description")
        content = _strip_html(description)
        articles.append(Article(
            title=title, content=content, url=link, fetched_at=datetime.now(timezone.utc),
        ))
    return articles


def _parse_atom(root: ET.Element, max_items: int) -> list[Article]:
    """Parse Atom feed."""
    articles = []
    for entry in root.findall(f"{_ATOM_NS}entry")[:max_items]:
        title = _text(entry, f"{_ATOM_NS}title")
        link_el = entry.find(f"{_ATOM_NS}link")
        link = link_el.get("href", "") if link_el is not None else ""
        summary = _text(entry, f"{_ATOM_NS}summary")
        content_el = entry.find(f"{_ATOM_NS}content")
        content = _strip_html(content_el.text or "") if content_el is not None else summary
        articles.append(Article(
            title=title, content=content or summary, url=link, fetched_at=datetime.now(timezone.utc),
        ))
    return articles


def _text(parent: ET.Element, tag: str) -> str:
    """Safely extract text from an XML element."""
    el = parent.find(tag)
    return (el.text or "").strip() if el is not None else ""


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", " ", text).strip()
