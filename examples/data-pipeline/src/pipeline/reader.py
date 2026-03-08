"""Data reading for the Data Pipeline workflow (data read layer).

Loads datasets from CSV/JSON files or generates sample data.
In a production workflow, this would connect to a database or API.
"""

import csv
import json
from io import StringIO
from pathlib import Path

from pipeline.models import Dataset, Record


def from_dicts(headers: list[str], rows: list[dict[str, str]]) -> Dataset:
    """Create a Dataset from a list of dicts."""
    return Dataset(
        headers=headers,
        records=[Record(data=row) for row in rows],
    )


def read_csv(path: Path) -> Dataset:
    """Read a CSV file into a Dataset. Returns empty Dataset if file not found."""
    if not path.exists():
        return Dataset(headers=[], records=[])
    text = path.read_text()
    if not text.strip():
        return Dataset(headers=[], records=[])
    reader = csv.DictReader(StringIO(text))
    headers = reader.fieldnames or []
    records = [Record(data=dict(row)) for row in reader]
    return Dataset(headers=list(headers), records=records)


def read_json(path: Path) -> Dataset:
    """Read a JSON array of objects into a Dataset. Returns empty Dataset if file not found."""
    if not path.exists():
        return Dataset(headers=[], records=[])
    data = json.loads(path.read_text())
    if not data:
        return Dataset(headers=[], records=[])
    headers = list(data[0].keys())
    records = [Record(data={k: str(v) for k, v in row.items()}) for row in data]
    return Dataset(headers=headers, records=records)


def generate_sample_data() -> Dataset:
    """Generate a realistic sample sales dataset."""
    regions = ["EMEA", "APAC", "NA", "LATAM"]
    products = ["Widget A", "Widget B", "Widget C", "Service X", "Service Y"]

    rows: list[dict[str, str]] = []
    base_prices = {"Widget A": 120, "Widget B": 85, "Widget C": 200, "Service X": 350, "Service Y": 150}

    for month in range(1, 7):
        for region in regions:
            for product in products:
                units = (hash(f"{month}{region}{product}") % 40) + 5
                price = base_prices[product]
                # Vary by region
                multiplier = {"EMEA": 1.0, "APAC": 0.9, "NA": 1.1, "LATAM": 0.8}[region]
                revenue = round(units * price * multiplier)
                rows.append({
                    "date": f"2026-{month:02d}-01",
                    "region": region,
                    "product": product,
                    "units": str(units),
                    "revenue": str(revenue),
                    "category": "hardware" if product.startswith("Widget") else "services",
                })

    headers = ["date", "region", "product", "units", "revenue", "category"]
    return from_dicts(headers, rows)
