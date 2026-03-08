"""Tests for notify_workflow.notify."""

from datetime import datetime

from notify_workflow.models import Event, Notification, Schedule, Rule
from notify_workflow.notify import format_digest, format_notification, save_digest


class TestFormatNotification:
    def test_includes_urgency_and_message(self):
        event = Event(
            title="Deploy",
            due_at=datetime(2026, 3, 8, 14, 0),
            priority="high",
            category="deadline",
        )
        notif = Notification(
            event=event,
            rule_name="test",
            urgency="critical",
            message="Deploy (due in 2h)",
        )
        result = format_notification(notif)
        assert "Deploy" in result
        assert "CRITICAL" in result or "!!!" in result


class TestFormatDigest:
    def test_includes_schedule_name(self):
        schedule = Schedule(
            name="Test Schedule",
            description="Testing",
            rules=[Rule(name="r", description="d", match_categories=["x"])],
        )
        result = format_digest([], schedule)
        assert "Test Schedule" in result

    def test_includes_no_notifications_message(self):
        schedule = Schedule(
            name="Test",
            description="Testing",
            rules=[Rule(name="r", description="d", match_categories=["x"])],
        )
        result = format_digest([], schedule)
        assert "No notifications" in result or "no matching" in result.lower()

    def test_includes_notifications(self):
        event = Event(
            title="Meeting",
            due_at=datetime(2026, 3, 8, 14, 0),
            priority="medium",
            category="meeting",
        )
        notif = Notification(event=event, rule_name="r", urgency="warning", message="Meeting (due in 4h)")
        schedule = Schedule(
            name="Test",
            description="Testing",
            rules=[Rule(name="r", description="d", match_categories=["meeting"])],
        )
        result = format_digest([notif], schedule)
        assert "Meeting" in result

    def test_includes_summary_counts(self):
        event = Event(title="A", due_at=datetime(2026, 3, 8, 14, 0), priority="high", category="deadline")
        notifications = [
            Notification(event=event, rule_name="r", urgency="critical", message="A"),
            Notification(event=event, rule_name="r", urgency="warning", message="B"),
        ]
        schedule = Schedule(
            name="Test",
            description="Testing",
            rules=[Rule(name="r", description="d", match_categories=["deadline"])],
        )
        result = format_digest(notifications, schedule)
        assert "1 critical" in result.lower()


class TestSaveDigest:
    def test_saves_to_file(self, tmp_path):
        path = save_digest("Test digest content", tmp_path, schedule_name="test")
        assert path.exists()
        assert path.read_text() == "Test digest content"

    def test_filename_contains_schedule_name(self, tmp_path):
        path = save_digest("Content", tmp_path, schedule_name="deadline-watch")
        assert "deadline-watch" in path.name

    def test_creates_output_dir(self, tmp_path):
        output = tmp_path / "subdir"
        path = save_digest("Content", output, schedule_name="test")
        assert path.exists()
