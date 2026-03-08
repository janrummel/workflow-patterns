#!/usr/bin/env python3
"""API Integration workflow runner.

Pattern: trigger -> api -> transform -> data

Fetches data from REST APIs, transforms JSON responses,
and saves structured results. Works offline with sample data.

Usage:
    uv run python run.py                      # interactive selection
    uv run python run.py --integration 1      # select by number
    uv run python run.py --format json        # save as JSON instead of CSV
    uv run python run.py --live               # force live API call (no fallback)
"""

import argparse
import os
import sys
from pathlib import Path

from api_workflow.client import fetch
from api_workflow.display import format_header, format_integration_menu, format_records_table
from api_workflow.integrations import INTEGRATIONS, get_integration
from api_workflow.storage import save_csv, save_json
from api_workflow.transform import transform_response

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


def _select_integration() -> int:
    """Interactive integration selection. Returns 0-based index."""
    print(format_header("API Integration — Setup"))
    print("Choose an integration:")
    print(format_integration_menu(INTEGRATIONS))
    print()
    try:
        choice = input(f"Integration (1-{len(INTEGRATIONS)}): ").strip()
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
        description="API Integration: trigger -> api -> transform -> data"
    )
    parser.add_argument(
        "--integration", type=int, default=None, help="Integration number (1-5)"
    )
    parser.add_argument(
        "--format", choices=["csv", "json"], default="csv", help="Output format (default: csv)"
    )
    parser.add_argument(
        "--live", action="store_true", help="Force live API call (no sample fallback)"
    )
    args = parser.parse_args()

    # Step 1: Trigger — select integration
    if args.integration is not None:
        integration = get_integration(args.integration - 1)
    else:
        integration = get_integration(_select_integration())

    print(f"\n── {integration.name} ──\n")

    # Step 2: API — fetch data
    sample = None if args.live else integration.sample_response
    print(f"  Fetching from {integration.api.base_url}...")
    response = fetch(integration.api, sample_data=sample)

    if not response.is_success:
        print(f"  Error: API request failed (status {response.status})")
        sys.exit(1)

    print(f"  Source: {response.source}")

    # Step 3: Transform — reshape response
    records = transform_response(response.data, integration.transform)
    print(f"  Extracted {len(records)} records\n")

    # Step 4: Data — save results
    print(format_header("Results"))
    print(format_records_table(records))

    slug = integration.name.lower().replace(" ", "-")
    if args.format == "json":
        path = save_json(records, OUTPUT_DIR, slug)
    else:
        path = save_csv(records, OUTPUT_DIR, slug)

    print(f"\n  Results saved to {path}\n")


if __name__ == "__main__":
    main()
