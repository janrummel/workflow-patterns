"""Tests for notify_workflow.schedules."""

from notify_workflow.models import Schedule
from notify_workflow.schedules import SCHEDULES, get_schedule


class TestSchedules:
    def test_five_schedules_defined(self):
        assert len(SCHEDULES) == 5

    def test_all_are_schedule_instances(self):
        for s in SCHEDULES:
            assert isinstance(s, Schedule)

    def test_all_have_rules(self):
        for s in SCHEDULES:
            assert len(s.rules) >= 1, f"{s.name} has no rules"

    def test_schedule_names_unique(self):
        names = [s.name for s in SCHEDULES]
        assert len(names) == len(set(names))

    def test_get_schedule_by_index(self):
        schedule = get_schedule(0)
        assert schedule == SCHEDULES[0]

    def test_get_schedule_clamps_negative(self):
        schedule = get_schedule(-1)
        assert schedule == SCHEDULES[0]

    def test_get_schedule_clamps_overflow(self):
        schedule = get_schedule(99)
        assert schedule == SCHEDULES[-1]
