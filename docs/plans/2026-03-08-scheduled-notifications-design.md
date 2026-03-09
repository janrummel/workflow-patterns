# Scheduled Notifications Example — Design

**Date:** 2026-03-08
**Pattern:** `trigger → api → logic → deliver`
**Status:** Approved

## Goal

Fourth runnable example for workflow-patterns. A notification scheduling system that loads events from schedule files, applies conditional rules to determine which notifications to fire, and delivers formatted notification digests. Demonstrates the `api → logic` pattern — data fetching followed by conditional branching.

## Architecture

```
select_schedule() → load_events() → evaluate_rules() → deliver_notifications()
trigger             api              logic              deliver
```

## Module Structure

```
examples/scheduled-notifications/
├── run.py                      # CLI entry point
├── .env.example                # Optional config (not needed for default mode)
├── .gitignore                  # .env, __pycache__, output/
├── pyproject.toml              # Zero runtime dependencies (stdlib only)
├── src/notify_workflow/
│   ├── __init__.py
│   ├── models.py               # Dataclasses: Event, Rule, Notification, Schedule
│   ├── schedules.py            # 5 schedule presets with rules
│   ├── sources.py              # Load events from JSON files (API layer)
│   ├── rules.py                # Rule evaluation engine (logic layer)
│   ├── notify.py               # Format and deliver notifications (file/terminal)
│   └── display.py              # Terminal formatting
├── tests/
│   ├── test_models.py
│   ├── test_schedules.py
│   ├── test_sources.py
│   ├── test_rules.py
│   ├── test_notify.py
│   ├── test_display.py
│   └── __init__.py
├── data/                       # Sample event files (JSON)
│   └── sample_events.json
└── output/                     # Generated notification digests
```

## Modules

### models.py

```python
@dataclass
class Event:
    title: str
    due_at: datetime
    priority: str       # "high", "medium", "low"
    category: str       # "meeting", "deadline", "reminder", "maintenance"
    tags: list[str]

@dataclass
class Rule:
    name: str
    description: str
    match_categories: list[str]         # event categories to match
    time_window_hours: int              # how far ahead to look
    include_overdue: bool               # also match past-due events
    min_priority: str                   # minimum priority level

@dataclass
class Notification:
    event: Event
    rule_name: str
    urgency: str        # "critical", "warning", "info"
    message: str

@dataclass
class Schedule:
    name: str
    description: str
    rules: list[Rule]
```

### schedules.py

5 curated schedule presets, each with specific rules:

| Schedule | Focus |
|----------|-------|
| Morning Briefing | All events today, grouped by priority |
| Deadline Watch | Approaching and overdue deadlines only |
| Standup Prep | Open items and blockers for daily standup |
| Follow-up Tracker | Items awaiting response or action |
| Maintenance Alerts | System maintenance and downtime windows |

Interactive selection menu. Also available via `--schedule` flag.

### sources.py

- `load_events(path)` → Parse JSON file into list of Event objects
- `load_events_from_dict(data)` → Create events from a dict (for testing/presets)
- `generate_sample_events(reference_time)` → Generate realistic sample events relative to a timestamp
- Default: generates sample events if no file provided

### rules.py

- `evaluate_rules(events, rules, now)` → Apply rules to events, return matching Notifications
- `determine_urgency(event, now)` → Calculate urgency based on time-to-due and priority
- `filter_by_time_window(events, window_hours, now, include_overdue)` → Time-based filtering
- `filter_by_priority(events, min_priority)` → Priority threshold filtering
- `filter_by_category(events, categories)` → Category matching
- `sort_notifications(notifications)` → Sort by urgency, then due time

### notify.py

- `format_notification(notification)` → Single notification as formatted string
- `format_digest(notifications, schedule)` → Full digest with header, grouped sections
- `save_digest(digest, output_dir)` → Write to timestamped markdown file
- `print_digest(digest)` → Print to terminal

### display.py

- `format_header(title)` → Boxed ASCII header
- `format_schedule_menu(schedules)` → Numbered schedule list
- `format_event_summary(event)` → One-line event summary with urgency indicator
- `format_urgency_badge(urgency)` → Visual urgency markers: [!!!] / [!!] / [i]

## UX Flow

```
$ uv run python run.py

╔══════════════════════════════════════════╗
║     Scheduled Notifications — Setup     ║
╚══════════════════════════════════════════╝

Choose a schedule:
  1. Morning Briefing     All events today, grouped by priority
  2. Deadline Watch       Approaching and overdue deadlines
  3. Standup Prep         Open items and blockers
  4. Follow-up Tracker    Items awaiting response
  5. Maintenance Alerts   System maintenance windows

Schedule (1-5): 2

── Deadline Watch ──

Loading events...
  Found 8 events, applying rules...

╔══════════════════════════════════════════╗
║         Notification Digest             ║
╚══════════════════════════════════════════╝

[!!!] CRITICAL — API migration deadline (overdue by 2h)
[!!!] CRITICAL — Security patch deployment (due in 1h)
[!! ] WARNING  — Q1 report submission (due in 6h)
[ i ] INFO     — Team retrospective prep (due tomorrow)

Summary: 2 critical, 1 warning, 1 info

Digest saved to output/2026-03-08_deadline-watch.md
```

## Key Differences from Previous Examples

| Aspect | Email Automation | Scheduled Notifications |
|--------|-----------------|------------------------|
| Pattern | `trigger → transform → deliver` | `trigger → api → logic → deliver` |
| New step | — | Conditional logic (rule engine) |
| Data source | User input | JSON events (simulated API) |
| Processing | Template rendering | Rule evaluation + filtering |
| Output | Single email | Multi-notification digest |
| Complexity | Template substitution | Time-based + priority logic |

## Dependencies

- Zero runtime dependencies (stdlib only)
- `pytest` (dev)
- Uses `datetime`, `json`, `pathlib` from stdlib

## Testing Strategy

- Rule evaluation with various time/priority scenarios
- Edge cases: no matching events, all overdue, empty schedule
- Event loading from JSON and dict sources
- Sample event generation with deterministic reference time
- Notification sorting and urgency determination
- Display formatting (badges, menus, headers)
- File I/O for digest output (tmp_path)
- Target: ~25 tests
