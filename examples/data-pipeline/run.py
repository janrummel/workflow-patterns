#!/usr/bin/env python3
"""Data Pipeline workflow runner.

Pattern: trigger -> data -> transform -> data

Reads structured data, applies transformation pipelines
(filter, aggregate, sort, enrich), and writes results.

Usage:
    uv run python run.py                  # interactive pipeline selection
    uv run python run.py --pipeline 1     # select pipeline by number
    uv run python run.py --input data.csv # load from custom CSV file
    uv run python run.py --format json    # output as JSON instead of CSV
"""

import argparse
import os
import sys
from pathlib import Path

from pipeline.display import format_header, format_pipeline_menu, format_stats
from pipeline.pipelines import PIPELINES, get_pipeline
from pipeline.reader import generate_sample_data, read_csv, read_json
from pipeline.transforms import apply_pipeline
from pipeline.writer import to_table_string, write_csv, write_json

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


def _select_pipeline() -> int:
    """Interactive pipeline selection. Returns 0-based index."""
    print(format_header("Data Pipeline — Setup"))
    print("Choose a pipeline:")
    print(format_pipeline_menu(PIPELINES))
    print()
    try:
        choice = input(f"Pipeline (1-{len(PIPELINES)}): ").strip()
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
        description="Data Pipeline: trigger -> data -> transform -> data"
    )
    parser.add_argument(
        "--pipeline", type=int, default=None, help="Pipeline number (1-5)"
    )
    parser.add_argument(
        "--input", type=str, default=None, help="Path to input CSV or JSON file"
    )
    parser.add_argument(
        "--format", choices=["csv", "json"], default="csv", help="Output format (default: csv)"
    )
    args = parser.parse_args()

    # Step 1: Trigger — select pipeline
    if args.pipeline is not None:
        pipeline = get_pipeline(args.pipeline - 1)
    else:
        pipeline = get_pipeline(_select_pipeline())

    print(f"\n── {pipeline.name} ──\n")

    # Step 2: Data (read) — load dataset
    if args.input:
        input_path = Path(args.input)
        if input_path.suffix == ".json":
            dataset = read_json(input_path)
        else:
            dataset = read_csv(input_path)
        if dataset.row_count == 0:
            print(f"  No data found in {input_path}")
            sys.exit(1)
        print(f"  Loaded from {input_path}")
    else:
        dataset = generate_sample_data()
        print("  Using generated sample data")

    print(format_stats(dataset))

    # Step 3: Transform — apply pipeline steps
    print(f"\n  Applying {len(pipeline.steps)} step(s):\n")
    result = apply_pipeline(dataset, pipeline.steps)

    for sr in result.step_results:
        print(f"    ✓ {sr.step_name}: {sr.input_count} → {sr.output_count} records")

    # Step 4: Data (write) — save results
    print(format_header("Results"))
    print(to_table_string(result.dataset))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = pipeline.name.lower().replace(" ", "-")
    if args.format == "json":
        path = write_json(result.dataset, OUTPUT_DIR / f"{slug}.json")
    else:
        path = write_csv(result.dataset, OUTPUT_DIR / f"{slug}.csv")

    print(f"\n  Results saved to {path}\n")


if __name__ == "__main__":
    main()
