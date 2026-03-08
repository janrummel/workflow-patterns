"""Domain models for the Scheduled Notifications workflow."""

from dataclasses import dataclass, field
from datetime import datetime


PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}
URGENCY_ORDER = {"critical": 3, "warning": 2, "info": 1}


@dataclass
class Event:
    title: str
    due_at: datetime
    priority: str  # "high", "medium", "low"
    category: str  # "meeting", "deadline", "reminder", "maintenance"
    tags: list[str] = field(default_factory=list)

    def is_overdue(self, now: datetime) -> bool:
        return self.due_at < now

    def hours_until(self, now: datetime) -> float:
        delta = self.due_at - now
        return delta.total_seconds() / 3600


@dataclass
class Rule:
    name: str
    description: str
    match_categories: list[str]
    time_window_hours: int = 24
    include_overdue: bool = False
    min_priority: str = "low"


@dataclass
class Notification:
    event: Event
    rule_name: str
    urgency: str  # "critical", "warning", "info"
    message: str


@dataclass
class Schedule:
    name: str
    description: str
    rules: list[Rule]
