"""Tests for notify_workflow.sources."""

import json
from datetime import datetime

from notify_workflow.models import Event
from notify_workflow.sources import (
    generate_sample_events,
    load_events,
    load_events_from_dicts,
)


class TestLoadEventsFromDicts:
    def test_load_single_event(self):
        data = [
            {
                "title": "Deploy",
                "due_at": "2026-03-08T14:00:00",
                "priority": "high",
                "category": "deadline",
                "tags": ["prod"],
            }
        ]
        events = load_events_from_dicts(data)
        assert len(events) == 1
        assert events[0].title == "Deploy"
        assert events[0].priority == "high"
        assert events[0].tags == ["prod"]

    def test_load_multiple_events(self):
        data = [
            {"title": "A", "due_at": "2026-03-08T10:00:00", "priority": "low", "category": "meeting"},
            {"title": "B", "due_at": "2026-03-08T12:00:00", "priority": "high", "category": "deadline"},
        ]
        events = load_events_from_dicts(data)
        assert len(events) == 2

    def test_load_event_default_tags(self):
        data = [
            {"title": "No tags", "due_at": "2026-03-08T10:00:00", "priority": "low", "category": "meeting"}
        ]
        events = load_events_from_dicts(data)
        assert events[0].tags == []

    def test_load_empty_list(self):
        assert load_events_from_dicts([]) == []


class TestLoadEvents:
    def test_load_from_json_file(self, tmp_path):
        data = [
            {"title": "From file", "due_at": "2026-03-08T09:00:00", "priority": "medium", "category": "reminder"}
        ]
        path = tmp_path / "events.json"
        path.write_text(json.dumps(data))
        events = load_events(path)
        assert len(events) == 1
        assert events[0].title == "From file"

    def test_load_nonexistent_file(self, tmp_path):
        path = tmp_path / "missing.json"
        events = load_events(path)
        assert events == []


class TestGenerateSampleEvents:
    def test_generates_events(self):
        ref = datetime(2026, 3, 8, 9, 0)
        events = generate_sample_events(ref)
        assert len(events) >= 6

    def test_all_are_event_instances(self):
        ref = datetime(2026, 3, 8, 9, 0)
        events = generate_sample_events(ref)
        for e in events:
            assert isinstance(e, Event)

    def test_includes_multiple_categories(self):
        ref = datetime(2026, 3, 8, 9, 0)
        events = generate_sample_events(ref)
        categories = {e.category for e in events}
        assert len(categories) >= 3

    def test_includes_multiple_priorities(self):
        ref = datetime(2026, 3, 8, 9, 0)
        events = generate_sample_events(ref)
        priorities = {e.priority for e in events}
        assert len(priorities) >= 2
