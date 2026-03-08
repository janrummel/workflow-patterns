"""Tests for notify_workflow.models."""

from datetime import datetime

from notify_workflow.models import Event, Notification, Rule, Schedule


class TestEvent:
    def test_create_event(self):
        event = Event(
            title="Deploy v2.0",
            due_at=datetime(2026, 3, 8, 14, 0),
            priority="high",
            category="deadline",
            tags=["deploy", "prod"],
        )
        assert event.title == "Deploy v2.0"
        assert event.priority == "high"
        assert event.category == "deadline"
        assert event.tags == ["deploy", "prod"]

    def test_event_default_tags(self):
        event = Event(
            title="Standup",
            due_at=datetime(2026, 3, 8, 9, 0),
            priority="low",
            category="meeting",
        )
        assert event.tags == []

    def test_event_is_overdue(self):
        past = datetime(2026, 3, 7, 10, 0)
        event = Event(title="Past", due_at=past, priority="high", category="deadline")
        now = datetime(2026, 3, 8, 10, 0)
        assert event.is_overdue(now) is True

    def test_event_is_not_overdue(self):
        future = datetime(2026, 3, 9, 10, 0)
        event = Event(title="Future", due_at=future, priority="low", category="meeting")
        now = datetime(2026, 3, 8, 10, 0)
        assert event.is_overdue(now) is False

    def test_event_hours_until(self):
        event = Event(
            title="Meeting",
            due_at=datetime(2026, 3, 8, 16, 0),
            priority="medium",
            category="meeting",
        )
        now = datetime(2026, 3, 8, 10, 0)
        assert event.hours_until(now) == 6.0

    def test_event_hours_until_negative_when_overdue(self):
        event = Event(
            title="Past",
            due_at=datetime(2026, 3, 8, 8, 0),
            priority="high",
            category="deadline",
        )
        now = datetime(2026, 3, 8, 10, 0)
        assert event.hours_until(now) == -2.0


class TestRule:
    def test_create_rule(self):
        rule = Rule(
            name="deadline_alert",
            description="Alert for approaching deadlines",
            match_categories=["deadline"],
            time_window_hours=24,
            include_overdue=True,
            min_priority="low",
        )
        assert rule.name == "deadline_alert"
        assert rule.time_window_hours == 24
        assert rule.include_overdue is True

    def test_rule_defaults(self):
        rule = Rule(
            name="simple",
            description="Simple rule",
            match_categories=["meeting"],
        )
        assert rule.time_window_hours == 24
        assert rule.include_overdue is False
        assert rule.min_priority == "low"


class TestNotification:
    def test_create_notification(self):
        event = Event(
            title="Deploy",
            due_at=datetime(2026, 3, 8, 14, 0),
            priority="high",
            category="deadline",
        )
        notif = Notification(
            event=event,
            rule_name="deadline_alert",
            urgency="critical",
            message="Deploy is due in 2 hours",
        )
        assert notif.urgency == "critical"
        assert notif.rule_name == "deadline_alert"


class TestSchedule:
    def test_create_schedule(self):
        rule = Rule(
            name="test",
            description="Test rule",
            match_categories=["meeting"],
        )
        schedule = Schedule(
            name="Morning Briefing",
            description="All events today",
            rules=[rule],
        )
        assert schedule.name == "Morning Briefing"
        assert len(schedule.rules) == 1
