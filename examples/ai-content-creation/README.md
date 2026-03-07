# AI Content Creation

**Pattern:** `api -> ai -> transform -> deliver`

Reads RSS/Atom feeds, summarizes articles with Claude, and produces a markdown digest.

## What It Does

```
[RSS Feeds] -> parse articles -> summarize with Claude -> format markdown -> save file
```

| Step | Category | Implementation |
|------|----------|---------------|
| Parse feeds | api | RSS/Atom XML parsing via `httpx` |
| Summarize | ai | Claude API (`claude-sonnet-4-5`) |
| Format digest | transform | Markdown generation |
| Save output | deliver | File write |

## Quick Start

```bash
cd examples/ai-content-creation
uv sync

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run with default feeds (simonwillison.net, lilianweng.github.io)
uv run python run.py

# Or specify your own feeds
uv run python run.py --feeds https://hnrss.org/newest?points=100 --title "HN Digest"
```

## Run Tests

```bash
uv run pytest -v
```

Tests run without an API key (Claude calls are mocked).

## Adapt This Pattern

This is a blueprint. Swap any step:

- **Different source**: Replace the feed URLs, or swap `fetch.py` for a database query or API call
- **Different AI**: Change the model in `summarize.py`, or add classification/extraction
- **Different format**: Generate HTML, PDF, or structured JSON instead of Markdown
- **Different delivery**: Send via email, post to Slack, or push to a CMS

The pattern stays the same: `api -> ai -> transform -> deliver`.
