"""Tests for notify_workflow.display."""

from notify_workflow.display import (
    format_header,
    format_schedule_menu,
    format_urgency_badge,
)
from notify_workflow.models import Rule, Schedule


class TestFormatHeader:
    def test_contains_title(self):
        result = format_header("Test Title")
        assert "Test Title" in result

    def test_has_box_chars(self):
        result = format_header("Test")
        assert "═" in result or "+" in result or "╔" in result


class TestFormatUrgencyBadge:
    def test_critical(self):
        badge = format_urgency_badge("critical")
        assert "!!!" in badge

    def test_warning(self):
        badge = format_urgency_badge("warning")
        assert "!!" in badge

    def test_info(self):
        badge = format_urgency_badge("info")
        assert "i" in badge


class TestFormatScheduleMenu:
    def test_lists_all_schedules(self):
        schedules = [
            Schedule(name="A", description="Desc A", rules=[
                Rule(name="r", description="d", match_categories=["x"])
            ]),
            Schedule(name="B", description="Desc B", rules=[
                Rule(name="r", description="d", match_categories=["x"])
            ]),
        ]
        result = format_schedule_menu(schedules)
        assert "1." in result
        assert "2." in result
        assert "A" in result
        assert "B" in result
