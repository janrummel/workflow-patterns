"""Data models for the content workflow."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    """A fetched article."""

    title: str
    content: str
    url: str
    fetched_at: datetime


@dataclass
class Summary:
    """An AI-generated summary of an article."""

    title: str
    summary_text: str
    original_url: str
