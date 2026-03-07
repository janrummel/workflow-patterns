"""Deliver step: output the digest to a file or stdout."""

from pathlib import Path


def deliver_to_file(content: str, path: Path) -> Path:
    """Write content to a file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path
