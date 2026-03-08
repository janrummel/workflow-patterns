#!/usr/bin/env python3
"""AI Content Creation workflow runner.

Pattern: api -> ai -> transform -> deliver

Reads RSS/Atom feeds, summarizes articles with Claude,
formats a markdown digest, and saves it to a file.

Usage:
    uv run python run.py                          # interactive feed selection
    uv run python run.py --feeds URL1 URL2        # custom feeds
    uv run python run.py --output digest.md       # custom output path
"""

import argparse
import os
from pathlib import Path

from content_workflow.deliver import deliver_to_file
from content_workflow.fetch import fetch_articles
from content_workflow.format import format_digest
from content_workflow.presets import CATEGORIES, CATEGORY_NAMES, estimate_cost, parse_selection
from content_workflow.summarize import summarize_articles


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


def _select_feeds_interactive() -> list[str]:
    """Interactive feed selection from curated presets."""
    print()
    print("╔══════════════════════════════════════════╗")
    print("║       AI Content Digest — Setup          ║")
    print("╚══════════════════════════════════════════╝")
    print()
    print("Choose a category:")
    print()
    for i, name in enumerate(CATEGORY_NAMES, 1):
        feeds = CATEGORIES[name]
        print(f"  {i}. {name}  ({len(feeds)} feeds)")
    print()

    cat_input = input(f"Category (1-{len(CATEGORY_NAMES)}): ").strip()
    cat_indices = parse_selection(cat_input, max_items=len(CATEGORY_NAMES))
    if not cat_indices:
        print("No category selected. Using AI & Machine Learning.")
        cat_indices = [0]
    cat_name = CATEGORY_NAMES[cat_indices[0]]
    feeds = CATEGORIES[cat_name]

    print()
    print(f"── {cat_name} ──")
    print()
    for i, feed in enumerate(feeds, 1):
        print(f"  {i:>2}. {feed.name:<35} {feed.description}")
    print()
    print("  Tip: 'all' for all, '1,3,5' for specific, '1-5' for range")
    print()

    feed_input = input("Select feeds: ").strip()
    if not feed_input:
        feed_input = "all"
    selected = parse_selection(feed_input, max_items=len(feeds))
    if not selected:
        print("No feeds selected. Using all.")
        selected = list(range(len(feeds)))

    chosen = [feeds[i] for i in selected]
    articles_estimate = len(chosen) * 3  # max_per_feed default

    print()
    print(f"  Selected: {len(chosen)} feed(s)")
    print(f"  {estimate_cost(articles_estimate)}")
    print()

    confirm = input("Continue? (Y/n): ").strip().lower()
    if confirm and confirm != "y":
        print("Aborted.")
        raise SystemExit(0)

    return [f.url for f in chosen]


def main():
    _load_dotenv()
    parser = argparse.ArgumentParser(description="AI Content Creation: feed -> summarize -> format -> deliver")
    parser.add_argument("--feeds", nargs="+", default=None, help="RSS/Atom feed URLs (skips interactive selection)")
    parser.add_argument("--output", type=Path, default=Path("output/digest.md"), help="Output file path")
    parser.add_argument("--title", default="AI Content Digest", help="Digest title")
    args = parser.parse_args()

    # Feed selection: interactive or explicit
    if args.feeds:
        feed_urls = args.feeds
    else:
        feed_urls = _select_feeds_interactive()

    # Step 1: API — fetch articles from RSS/Atom feeds
    print(f"Fetching from {len(feed_urls)} feed(s)...")
    articles = fetch_articles(feed_urls, max_per_feed=3)
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
