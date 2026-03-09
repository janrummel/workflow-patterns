"""Event sources for the Scheduled Notifications workflow (API layer).

Loads events from JSON files or generates sample data.
In a production workflow, this would call a calendar or task API.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from notify_workflow.models import Event


def load_events_from_dicts(data: list[dict]) -> list[Event]:
    """Create Event objects from a list of dicts."""
    events = []
    for item in data:
        events.append(
            Event(
                title=item["title"],
                due_at=datetime.fromisoformat(item["due_at"]),
                priority=item["priority"],
                category=item["category"],
                tags=item.get("tags", []),
            )
        )
    return events


def load_events(path: Path) -> list[Event]:
    """Load events from a JSON file. Returns empty list if file not found."""
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return load_events_from_dicts(data)


def generate_sample_events(reference_time: datetime) -> list[Event]:
    """Generate realistic sample events relative to a reference time."""
    return [
        Event(
            title="API migration deadline",
            due_at=reference_time + timedelta(hours=-2),
            priority="high",
            category="deadline",
            tags=["api", "migration"],
        ),
        Event(
            title="Security patch deployment",
            due_at=reference_time + timedelta(hours=1),
            priority="high",
            category="deadline",
            tags=["security", "deploy"],
        ),
        Event(
            title="Q1 report submission",
            due_at=reference_time + timedelta(hours=6),
            priority="medium",
            category="deadline",
            tags=["report", "q1"],
        ),
        Event(
            title="Team retrospective",
            due_at=reference_time + timedelta(hours=28),
            priority="low",
            category="meeting",
            tags=["team", "retro"],
        ),
        Event(
            title="Daily standup",
            due_at=reference_time + timedelta(hours=1, minutes=30),
            priority="medium",
            category="meeting",
            tags=["standup"],
        ),
        Event(
            title="Review PR #142",
            due_at=reference_time + timedelta(hours=3),
            priority="medium",
            category="reminder",
            tags=["code-review"],
        ),
        Event(
            title="Follow up with vendor",
            due_at=reference_time + timedelta(hours=-5),
            priority="low",
            category="reminder",
            tags=["vendor", "followup"],
        ),
        Event(
            title="Database maintenance window",
            due_at=reference_time + timedelta(hours=48),
            priority="high",
            category="maintenance",
            tags=["database", "downtime"],
        ),
        Event(
            title="SSL certificate renewal",
            due_at=reference_time + timedelta(hours=72),
            priority="medium",
            category="maintenance",
            tags=["ssl", "security"],
        ),
        Event(
            title="Client demo preparation",
            due_at=reference_time + timedelta(hours=4),
            priority="high",
            category="reminder",
            tags=["client", "demo"],
        ),
    ]
