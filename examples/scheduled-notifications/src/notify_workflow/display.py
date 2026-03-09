"""Terminal display formatting for the Scheduled Notifications workflow."""

from notify_workflow.models import Schedule


def format_header(title: str) -> str:
    """Create a boxed ASCII header."""
    width = max(len(title) + 8, 42)
    top = "╔" + "═" * width + "╗"
    mid = "║" + title.center(width) + "║"
    bot = "╚" + "═" * width + "╝"
    return f"\n{top}\n{mid}\n{bot}\n"


def format_urgency_badge(urgency: str) -> str:
    """Format urgency as a visual badge."""
    badges = {
        "critical": "[!!!]",
        "warning":  "[!! ]",
        "info":     "[ i ]",
    }
    return badges.get(urgency, "[   ]")


def format_urgency_label(urgency: str) -> str:
    """Format urgency as an uppercase label."""
    labels = {
        "critical": "CRITICAL",
        "warning":  "WARNING ",
        "info":     "INFO    ",
    }
    return labels.get(urgency, "UNKNOWN ")


def format_schedule_menu(schedules: list[Schedule]) -> str:
    """Format schedule selection menu."""
    lines = []
    for i, s in enumerate(schedules, 1):
        lines.append(f"  {i}. {s.name:<22s} {s.description}")
    return "\n".join(lines)
