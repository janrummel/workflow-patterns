"""Format step (transform): turn summaries into a markdown digest."""

from content_workflow.models import Summary


def format_digest(summaries: list[Summary], title: str = "Content Digest") -> str:
    """Format summaries into a markdown digest."""
    lines = [f"# {title}", ""]

    if not summaries:
        lines.append("No articles found for this digest.")
        return "\n".join(lines)

    for summary in summaries:
        lines.append(f"## {summary.title}")
        lines.append("")
        lines.append(summary.summary_text)
        lines.append("")
        lines.append(f"[Source]({summary.original_url})")
        lines.append("")

    return "\n".join(lines)
