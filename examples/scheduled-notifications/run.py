#!/usr/bin/env python3
"""Scheduled Notifications workflow runner.

Pattern: trigger -> api -> logic -> deliver

Loads scheduled events, applies notification rules based on
time windows and priorities, and delivers formatted digests.

Usage:
    uv run python run.py                  # interactive schedule selection
    uv run python run.py --schedule 2     # select schedule by number
    uv run python run.py --events data/events.json  # load events from file
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from notify_workflow.display import format_header, format_schedule_menu
from notify_workflow.notify import format_digest, format_notification, save_digest
from notify_workflow.rules import evaluate_rules
from notify_workflow.schedules import SCHEDULES, get_schedule
from notify_workflow.sources import generate_sample_events, load_events

OUTPUT_DIR = Path(__file__).parent / "output"


def _load_dotenv():
    """Load .env file if it exists."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if key and value:
            os.environ.setdefault(key.strip(), value.strip())


def _select_schedule() -> int:
    """Interactive schedule selection. Returns 0-based index."""
    print(format_header("Scheduled Notifications — Setup"))
    print("Choose a schedule:")
    print(format_schedule_menu(SCHEDULES))
    print()
    try:
        choice = input(f"Schedule (1-{len(SCHEDULES)}): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(0)
    try:
        return int(choice) - 1
    except ValueError:
        return 0


def main():
    _load_dotenv()

    parser = argparse.ArgumentParser(
        description="Scheduled Notifications: trigger -> api -> logic -> deliver"
    )
    parser.add_argument(
        "--schedule", type=int, default=None, help="Schedule number (1-5)"
    )
    parser.add_argument(
        "--events", type=str, default=None, help="Path to events JSON file"
    )
    args = parser.parse_args()

    # Step 1: Trigger — select schedule
    if args.schedule is not None:
        schedule = get_schedule(args.schedule - 1)
    else:
        schedule = get_schedule(_select_schedule())

    print(f"\n── {schedule.name} ──\n")

    # Step 2: API — load events
    now = datetime.now()
    if args.events:
        events_path = Path(args.events)
        events = load_events(events_path)
        if not events:
            print(f"  No events found in {events_path}")
            sys.exit(1)
        print(f"  Loaded {len(events)} events from {events_path}")
    else:
        events = generate_sample_events(now)
        print(f"  Generated {len(events)} sample events")

    # Step 3: Logic — evaluate rules
    print(f"  Applying {len(schedule.rules)} rule(s)...\n")
    notifications = evaluate_rules(events, schedule.rules, now)

    # Step 4: Deliver — format and save
    print(format_header("Notification Digest"))

    if not notifications:
        print("  No notifications match the current rules.\n")
    else:
        for n in notifications:
            print(f"  {format_notification(n)}")
        print()

        counts = {}
        for n in notifications:
            counts[n.urgency] = counts.get(n.urgency, 0) + 1
        summary = ", ".join(
            f"{c} {u}" for u, c in sorted(counts.items(), key=lambda x: -{"critical": 3, "warning": 2, "info": 1}.get(x[0], 0))
        )
        print(f"  Summary: {summary}\n")

    digest = format_digest(notifications, schedule)
    path = save_digest(digest, OUTPUT_DIR, schedule.name)
    print(f"  Digest saved to {path}\n")


if __name__ == "__main__":
    main()
