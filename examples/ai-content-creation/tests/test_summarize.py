"""Tests for the summarize step (ai)."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import anthropic
import pytest

from content_workflow.models import Article
from content_workflow.summarize import summarize_articles


def _make_article(title="Test", content="Some long article content here.", url="https://example.com"):
    return Article(title=title, content=content, url=url, fetched_at=datetime.now())


def _mock_claude_response(text: str):
    """Create a mock Anthropic Messages API response."""
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = text
    mock_response = MagicMock()
    mock_response.content = [mock_block]
    return mock_response


def test_summarize_single_article():
    """An article is summarized via Claude API, returning a Summary."""
    article = _make_article(title="AI News", content="Long article about AI breakthroughs...")

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_claude_response(
        "AI researchers have made significant breakthroughs."
    )

    with patch("content_workflow.summarize.anthropic.Anthropic", return_value=mock_client):
        summaries = summarize_articles([article])

    assert len(summaries) == 1
    assert summaries[0].title == "AI News"
    assert "breakthroughs" in summaries[0].summary_text
    assert summaries[0].original_url == "https://example.com"


def test_summarize_calls_claude_with_correct_model():
    """Claude API is called with claude-sonnet-4-5 (cost-effective for summarization)."""
    article = _make_article()

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_claude_response("Summary.")

    with patch("content_workflow.summarize.anthropic.Anthropic", return_value=mock_client):
        summarize_articles([article])

    call_kwargs = mock_client.messages.create.call_args
    assert call_kwargs.kwargs["model"] == "claude-sonnet-4-5"


def test_summarize_multiple_articles():
    """Multiple articles are each summarized independently."""
    articles = [
        _make_article(title="Article 1", content="Content 1"),
        _make_article(title="Article 2", content="Content 2"),
    ]

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [
        _mock_claude_response("Summary 1"),
        _mock_claude_response("Summary 2"),
    ]

    with patch("content_workflow.summarize.anthropic.Anthropic", return_value=mock_client):
        summaries = summarize_articles(articles)

    assert len(summaries) == 2
    assert summaries[0].title == "Article 1"
    assert summaries[1].title == "Article 2"


def test_summarize_missing_api_key():
    """A clear error is raised when ANTHROPIC_API_KEY is not set."""
    article = _make_article()

    with patch("content_workflow.summarize.anthropic.Anthropic") as mock_cls:
        mock_cls.side_effect = anthropic.AuthenticationError(
            message="No API key",
            response=MagicMock(status_code=401),
            body=None,
        )
        with pytest.raises(SystemExit):
            summarize_articles([article])
