"""Data storage for the API Integration workflow (data layer).

Saves transformed API results to CSV/JSON files.
"""

import csv
import json
from datetime import datetime
from pathlib import Path


def save_json(records: list[dict], output_dir: Path, name: str) -> Path:
    """Save records as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = output_dir / f"{timestamp}_{name}.json"
    path.write_text(json.dumps(records, indent=2, default=str))
    return path


def save_csv(records: list[dict], output_dir: Path, name: str) -> Path:
    """Save records as CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = output_dir / f"{timestamp}_{name}.csv"

    if not records:
        path.write_text("")
        return path

    headers = list(records[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rec in records:
            writer.writerow({h: rec.get(h, "") for h in headers})
    return path
