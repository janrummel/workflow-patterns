"""Schedule presets for the Scheduled Notifications workflow."""

from notify_workflow.models import Rule, Schedule

SCHEDULES: list[Schedule] = [
    Schedule(
        name="Morning Briefing",
        description="All events today, grouped by priority",
        rules=[
            Rule(
                name="today_all",
                description="Everything due within 16 hours",
                match_categories=["meeting", "deadline", "reminder", "maintenance"],
                time_window_hours=16,
                include_overdue=True,
                min_priority="low",
            ),
        ],
    ),
    Schedule(
        name="Deadline Watch",
        description="Approaching and overdue deadlines",
        rules=[
            Rule(
                name="deadline_urgent",
                description="Deadlines due within 4 hours or overdue",
                match_categories=["deadline"],
                time_window_hours=4,
                include_overdue=True,
                min_priority="medium",
            ),
            Rule(
                name="deadline_upcoming",
                description="Deadlines due within 24 hours",
                match_categories=["deadline"],
                time_window_hours=24,
                include_overdue=False,
                min_priority="low",
            ),
        ],
    ),
    Schedule(
        name="Standup Prep",
        description="Open items and blockers for daily standup",
        rules=[
            Rule(
                name="standup_blockers",
                description="Overdue items and high-priority tasks",
                match_categories=["deadline", "reminder"],
                time_window_hours=8,
                include_overdue=True,
                min_priority="medium",
            ),
            Rule(
                name="standup_meetings",
                description="Today's meetings",
                match_categories=["meeting"],
                time_window_hours=10,
                include_overdue=False,
                min_priority="low",
            ),
        ],
    ),
    Schedule(
        name="Follow-up Tracker",
        description="Items awaiting response or action",
        rules=[
            Rule(
                name="followup_overdue",
                description="Overdue reminders and deadlines",
                match_categories=["reminder", "deadline"],
                time_window_hours=0,
                include_overdue=True,
                min_priority="low",
            ),
            Rule(
                name="followup_upcoming",
                description="Reminders due within 48 hours",
                match_categories=["reminder"],
                time_window_hours=48,
                include_overdue=False,
                min_priority="low",
            ),
        ],
    ),
    Schedule(
        name="Maintenance Alerts",
        description="System maintenance and downtime windows",
        rules=[
            Rule(
                name="maintenance_soon",
                description="Maintenance events within 72 hours",
                match_categories=["maintenance"],
                time_window_hours=72,
                include_overdue=True,
                min_priority="low",
            ),
        ],
    ),
]


def get_schedule(index: int) -> Schedule:
    """Get schedule by index, clamping to valid range."""
    clamped = max(0, min(index, len(SCHEDULES) - 1))
    return SCHEDULES[clamped]
