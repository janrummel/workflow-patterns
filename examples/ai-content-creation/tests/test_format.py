"""Tests for the format step (transform)."""

from content_workflow.format import format_digest
from content_workflow.models import Summary


def test_format_single_summary():
    """A single summary produces a valid markdown digest."""
    summaries = [
        Summary(title="AI News", summary_text="Big breakthroughs in AI.", original_url="https://example.com/ai")
    ]

    result = format_digest(summaries, title="Weekly Digest")

    assert "# Weekly Digest" in result
    assert "## AI News" in result
    assert "Big breakthroughs in AI." in result
    assert "https://example.com/ai" in result


def test_format_multiple_summaries():
    """Multiple summaries are each listed as separate sections."""
    summaries = [
        Summary(title="Article 1", summary_text="Summary 1.", original_url="https://a.com"),
        Summary(title="Article 2", summary_text="Summary 2.", original_url="https://b.com"),
    ]

    result = format_digest(summaries, title="Digest")

    assert result.count("## ") == 2
    assert "Summary 1." in result
    assert "Summary 2." in result


def test_format_empty_summaries():
    """An empty list produces a digest with a 'no articles' note."""
    result = format_digest([], title="Empty Digest")

    assert "# Empty Digest" in result
    assert "no articles" in result.lower()
