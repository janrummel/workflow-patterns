"""Rule evaluation engine for the Scheduled Notifications workflow (logic layer).

Applies rules to events: filtering by time window, priority, and category,
then determines urgency and builds notifications.
"""

from datetime import datetime

from notify_workflow.models import (
    PRIORITY_ORDER,
    URGENCY_ORDER,
    Event,
    Notification,
    Rule,
)


def determine_urgency(event: Event, now: datetime) -> str:
    """Determine notification urgency based on time-to-due and priority."""
    hours = event.hours_until(now)
    is_high = event.priority == "high"

    if hours < 0:
        return "critical" if is_high else "warning"
    if hours <= 2:
        return "critical" if is_high else "warning"
    if hours <= 8:
        return "warning" if event.priority in ("high", "medium") else "info"
    return "info"


def filter_by_time_window(
    events: list[Event],
    window_hours: int,
    now: datetime,
    include_overdue: bool,
) -> list[Event]:
    """Filter events by time window relative to now."""
    result = []
    for event in events:
        hours = event.hours_until(now)
        if hours < 0 and include_overdue:
            result.append(event)
        elif 0 <= hours <= window_hours:
            result.append(event)
    return result


def filter_by_priority(events: list[Event], min_priority: str) -> list[Event]:
    """Filter events at or above minimum priority level."""
    threshold = PRIORITY_ORDER.get(min_priority, 1)
    return [e for e in events if PRIORITY_ORDER.get(e.priority, 1) >= threshold]


def filter_by_category(events: list[Event], categories: list[str]) -> list[Event]:
    """Filter events matching any of the given categories."""
    cat_set = set(categories)
    return [e for e in events if e.category in cat_set]


def evaluate_rules(
    events: list[Event], rules: list[Rule], now: datetime
) -> list[Notification]:
    """Apply all rules to events and return deduplicated notifications."""
    seen_titles: set[str] = set()
    notifications: list[Notification] = []

    for rule in rules:
        matched = filter_by_category(events, rule.match_categories)
        matched = filter_by_priority(matched, rule.min_priority)
        matched = filter_by_time_window(
            matched, rule.time_window_hours, now, rule.include_overdue
        )

        for event in matched:
            if event.title in seen_titles:
                continue
            seen_titles.add(event.title)

            urgency = determine_urgency(event, now)
            hours = event.hours_until(now)
            if hours < 0:
                msg = f"{event.title} (overdue by {abs(hours):.0f}h)"
            elif hours < 1:
                msg = f"{event.title} (due in {hours * 60:.0f}min)"
            else:
                msg = f"{event.title} (due in {hours:.0f}h)"

            notifications.append(
                Notification(
                    event=event,
                    rule_name=rule.name,
                    urgency=urgency,
                    message=msg,
                )
            )

    return sort_notifications(notifications)


def sort_notifications(notifications: list[Notification]) -> list[Notification]:
    """Sort by urgency (critical first), then by due time (soonest first)."""
    return sorted(
        notifications,
        key=lambda n: (-URGENCY_ORDER.get(n.urgency, 0), n.event.due_at),
    )
