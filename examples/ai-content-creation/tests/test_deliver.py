"""Tests for the deliver step."""

from pathlib import Path

from content_workflow.deliver import deliver_to_file


def test_deliver_to_file(tmp_path):
    """Content is written to the specified file path."""
    output = tmp_path / "digest.md"
    content = "# My Digest\n\nSome content here."

    result = deliver_to_file(content, output)

    assert result == output
    assert output.read_text() == content


def test_deliver_creates_parent_dirs(tmp_path):
    """Parent directories are created if they don't exist."""
    output = tmp_path / "nested" / "dir" / "digest.md"
    content = "# Nested Digest"

    result = deliver_to_file(content, output)

    assert result.exists()
    assert result.read_text() == content
