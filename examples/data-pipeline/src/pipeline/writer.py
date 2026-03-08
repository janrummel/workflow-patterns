"""Data writing for the Data Pipeline workflow (data write layer).

Saves datasets to CSV/JSON files and formats ASCII tables.
"""

import csv
import json
from io import StringIO
from pathlib import Path

from pipeline.models import Dataset


def write_csv(dataset: Dataset, path: Path) -> Path:
    """Write dataset to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=dataset.headers)
        writer.writeheader()
        for rec in dataset.records:
            writer.writerow({h: rec.data.get(h, "") for h in dataset.headers})
    return path


def write_json(dataset: Dataset, path: Path) -> Path:
    """Write dataset to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [{h: rec.data.get(h, "") for h in dataset.headers} for rec in dataset.records]
    path.write_text(json.dumps(data, indent=2))
    return path


def to_table_string(dataset: Dataset, max_rows: int = 15) -> str:
    """Format dataset as an ASCII table."""
    if not dataset.headers:
        return "(empty dataset)"

    if dataset.row_count == 0:
        header_line = " | ".join(dataset.headers)
        return f"{header_line}\n(no records)"

    # Calculate column widths
    widths = {h: len(h) for h in dataset.headers}
    display_records = dataset.records[:max_rows]
    for rec in display_records:
        for h in dataset.headers:
            widths[h] = max(widths[h], len(rec.data.get(h, "")))

    # Build table
    def row_str(values: dict[str, str]) -> str:
        cells = [values.get(h, "").ljust(widths[h]) for h in dataset.headers]
        return "│ " + " │ ".join(cells) + " │"

    sep_top = "┌─" + "─┬─".join("─" * widths[h] for h in dataset.headers) + "─┐"
    sep_mid = "├─" + "─┼─".join("─" * widths[h] for h in dataset.headers) + "─┤"
    sep_bot = "└─" + "─┴─".join("─" * widths[h] for h in dataset.headers) + "─┘"

    header_vals = {h: h for h in dataset.headers}
    lines = [sep_top, row_str(header_vals), sep_mid]
    for rec in display_records:
        lines.append(row_str(rec.data))
    lines.append(sep_bot)

    if dataset.row_count > max_rows:
        remaining = dataset.row_count - max_rows
        lines.append(f"... and {remaining} more rows")

    return "\n".join(lines)
