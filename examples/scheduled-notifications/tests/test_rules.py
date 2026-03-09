"""Tests for notify_workflow.rules."""

from datetime import datetime, timedelta

from notify_workflow.models import Event, Notification, Rule
from notify_workflow.rules import (
    determine_urgency,
    evaluate_rules,
    filter_by_category,
    filter_by_priority,
    filter_by_time_window,
    sort_notifications,
)

NOW = datetime(2026, 3, 8, 10, 0)


def _event(title="Test", hours_offset=2, priority="medium", category="deadline"):
    return Event(
        title=title,
        due_at=NOW + timedelta(hours=hours_offset),
        priority=priority,
        category=category,
    )


class TestDetermineUrgency:
    def test_overdue_high_is_critical(self):
        event = _event(hours_offset=-1, priority="high")
        assert determine_urgency(event, NOW) == "critical"

    def test_overdue_low_is_warning(self):
        event = _event(hours_offset=-1, priority="low")
        assert determine_urgency(event, NOW) == "warning"

    def test_due_soon_high_is_critical(self):
        event = _event(hours_offset=1, priority="high")
        assert determine_urgency(event, NOW) == "critical"

    def test_due_soon_medium_is_warning(self):
        event = _event(hours_offset=2, priority="medium")
        assert determine_urgency(event, NOW) == "warning"

    def test_far_future_low_is_info(self):
        event = _event(hours_offset=20, priority="low")
        assert determine_urgency(event, NOW) == "info"


class TestFilterByTimeWindow:
    def test_includes_events_within_window(self):
        events = [_event(hours_offset=2), _event(hours_offset=5)]
        result = filter_by_time_window(events, window_hours=6, now=NOW, include_overdue=False)
        assert len(result) == 2

    def test_excludes_events_outside_window(self):
        events = [_event(hours_offset=10)]
        result = filter_by_time_window(events, window_hours=6, now=NOW, include_overdue=False)
        assert len(result) == 0

    def test_excludes_overdue_when_not_included(self):
        events = [_event(hours_offset=-2)]
        result = filter_by_time_window(events, window_hours=6, now=NOW, include_overdue=False)
        assert len(result) == 0

    def test_includes_overdue_when_included(self):
        events = [_event(hours_offset=-2)]
        result = filter_by_time_window(events, window_hours=6, now=NOW, include_overdue=True)
        assert len(result) == 1


class TestFilterByPriority:
    def test_filter_minimum_high(self):
        events = [_event(priority="high"), _event(priority="medium"), _event(priority="low")]
        result = filter_by_priority(events, "high")
        assert len(result) == 1

    def test_filter_minimum_medium(self):
        events = [_event(priority="high"), _event(priority="medium"), _event(priority="low")]
        result = filter_by_priority(events, "medium")
        assert len(result) == 2

    def test_filter_minimum_low(self):
        events = [_event(priority="high"), _event(priority="medium"), _event(priority="low")]
        result = filter_by_priority(events, "low")
        assert len(result) == 3


class TestFilterByCategory:
    def test_single_category(self):
        events = [_event(category="deadline"), _event(category="meeting")]
        result = filter_by_category(events, ["deadline"])
        assert len(result) == 1

    def test_multiple_categories(self):
        events = [_event(category="deadline"), _event(category="meeting"), _event(category="reminder")]
        result = filter_by_category(events, ["deadline", "meeting"])
        assert len(result) == 2

    def test_no_match(self):
        events = [_event(category="meeting")]
        result = filter_by_category(events, ["deadline"])
        assert len(result) == 0


class TestEvaluateRules:
    def test_basic_rule_evaluation(self):
        events = [_event(hours_offset=2, category="deadline", priority="high")]
        rules = [
            Rule(
                name="test_rule",
                description="Test",
                match_categories=["deadline"],
                time_window_hours=6,
                include_overdue=False,
                min_priority="low",
            )
        ]
        result = evaluate_rules(events, rules, NOW)
        assert len(result) == 1
        assert result[0].rule_name == "test_rule"

    def test_no_matching_events(self):
        events = [_event(hours_offset=2, category="meeting")]
        rules = [
            Rule(name="deadline_only", description="Test", match_categories=["deadline"])
        ]
        result = evaluate_rules(events, rules, NOW)
        assert len(result) == 0

    def test_deduplicates_across_rules(self):
        event = _event(hours_offset=2, category="deadline", priority="high")
        rules = [
            Rule(name="rule1", description="Test 1", match_categories=["deadline"], time_window_hours=6),
            Rule(name="rule2", description="Test 2", match_categories=["deadline"], time_window_hours=24),
        ]
        result = evaluate_rules([event], rules, NOW)
        assert len(result) == 1  # same event, first matching rule wins


class TestSortNotifications:
    def test_sort_by_urgency_then_time(self):
        n1 = Notification(event=_event(hours_offset=5), rule_name="r", urgency="info", message="")
        n2 = Notification(event=_event(hours_offset=1), rule_name="r", urgency="critical", message="")
        n3 = Notification(event=_event(hours_offset=3), rule_name="r", urgency="warning", message="")
        result = sort_notifications([n1, n2, n3])
        assert [n.urgency for n in result] == ["critical", "warning", "info"]
