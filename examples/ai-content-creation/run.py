#!/usr/bin/env python3
"""AI Content Creation workflow runner.

Pattern: api -> ai -> transform -> deliver

Reads RSS/Atom feeds, summarizes articles with Claude,
formats a markdown digest, and saves it to a file.

Usage:
    uv run python run.py
    uv run python run.py --feeds https://hnrss.org/newest?points=100
    uv run python run.py --output digest.md --title "My Digest"
"""

import argparse
import os
from pathlib import Path

from content_workflow.deliver import deliver_to_file
from content_workflow.fetch import fetch_articles
from content_workflow.format import format_digest
from content_workflow.summarize import summarize_articles

DEFAULT_FEEDS = [
    "https://simonwillison.net/atom/everything/",
    "https://lilianweng.github.io/index.xml",
]


def _load_dotenv():
    """Load .env file if it exists (no external dependency needed)."""
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


def main():
    _load_dotenv()
    parser = argparse.ArgumentParser(description="AI Content Creation: feed -> summarize -> format -> deliver")
    parser.add_argument("--feeds", nargs="+", default=DEFAULT_FEEDS, help="RSS/Atom feed URLs")
    parser.add_argument("--output", type=Path, default=Path("output/digest.md"), help="Output file path")
    parser.add_argument("--title", default="AI Content Digest", help="Digest title")
    args = parser.parse_args()

    # Step 1: API — fetch articles from RSS/Atom feeds
    print(f"Fetching from {len(args.feeds)} feed(s)...")
    articles = fetch_articles(args.feeds, max_per_feed=3)
    print(f"  Got {len(articles)} article(s)")

    if not articles:
        print("No articles fetched. Exiting.")
        return

    # Step 2: AI — summarize with Claude
    print("Summarizing with Claude...")
    summaries = summarize_articles(articles)
    print(f"  Generated {len(summaries)} summaries")

    # Step 3: Transform — format digest
    digest = format_digest(summaries, title=args.title)

    # Step 4: Deliver — save to file
    path = deliver_to_file(digest, args.output)
    print(f"Digest saved to {path}")
    print()
    print(digest)


if __name__ == "__main__":
    main()
