"""Notification formatting and delivery for the Scheduled Notifications workflow (deliver layer)."""

from datetime import datetime
from pathlib import Path

from notify_workflow.display import format_urgency_badge, format_urgency_label
from notify_workflow.models import Notification, Schedule


def format_notification(notification: Notification) -> str:
    """Format a single notification as a display line."""
    badge = format_urgency_badge(notification.urgency)
    label = format_urgency_label(notification.urgency)
    return f"{badge} {label} — {notification.message}"


def format_digest(notifications: list[Notification], schedule: Schedule) -> str:
    """Format a full notification digest."""
    lines = [f"# {schedule.name}", f"_{schedule.description}_", ""]

    if not notifications:
        lines.append("No notifications match the current rules.")
        return "\n".join(lines)

    for n in notifications:
        lines.append(format_notification(n))

    lines.append("")

    counts = {}
    for n in notifications:
        counts[n.urgency] = counts.get(n.urgency, 0) + 1

    summary_parts = []
    for urgency in ("critical", "warning", "info"):
        if urgency in counts:
            summary_parts.append(f"{counts[urgency]} {urgency}")
    lines.append(f"Summary: {', '.join(summary_parts)}")

    return "\n".join(lines)


def save_digest(digest: str, output_dir: Path, schedule_name: str) -> Path:
    """Save digest to a timestamped markdown file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = schedule_name.lower().replace(" ", "-")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = output_dir / f"{timestamp}_{slug}.md"
    path.write_text(digest)
    return path
