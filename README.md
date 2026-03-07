# Workflow Patterns

Analyze 7,000+ real-world automation workflows to extract recurring patterns — and translate them into Claude Code architectures.

## What it does

1. **Parses** n8n workflow JSONs into abstract graph models (nodes + edges)
2. **Analyzes** patterns across workflows (categories, connections, frequency)
3. **Translates** patterns into Claude Code building blocks (MCP servers, skills, agents, scripts)
4. **Serves** everything as an MCP server that Claude can query

## Why

People build automation workflows in tools like n8n every day. The patterns behind these workflows (trigger -> transform -> deliver, etc.) are universal — they apply regardless of the platform.

This project extracts those patterns from 7,000+ real workflows and helps you implement them with Claude Code instead of a drag-and-drop UI.

## Quick Start

```bash
git clone https://github.com/janrummel/workflow-patterns
cd workflow-patterns
uv sync
uv run pytest -v
```

### Use as MCP server with Claude Code

```bash
claude --mcp-config mcp.json
```

Then ask Claude:

> "I want to build a workflow that fetches news articles weekly, summarizes them with AI, and sends a digest by email."

Claude will use the MCP tools to find matching patterns and suggest a Claude Code architecture.

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_patterns(query)` | Find patterns matching a natural language description |
| `suggest_implementation(pattern)` | Get Claude Code architecture for a pattern |
| `list_categories()` | Show category statistics and common connections |
| `show_all_patterns()` | List all unique patterns ranked by frequency |

## Pattern Categories

Workflows are decomposed into abstract categories:

| Category | What it represents | Claude Code equivalent |
|----------|-------------------|----------------------|
| trigger | Event or schedule that starts the workflow | Cron job, file watcher |
| ai | LLM processing (summarize, analyze, generate) | Claude agent |
| transform | Data reshaping, filtering, enrichment | Python script |
| deliver | Send output (email, Slack, webhook) | MCP server |
| data | Read/write database or spreadsheet | MCP server |
| api | Call external HTTP APIs | MCP server |
| logic | Conditional branching, routing | Claude skill |
| storage | File storage (Drive, S3, local) | MCP server |

## Project Structure

```
workflow-patterns/
├── src/workflow_patterns/
│   ├── models.py              # Data models (Node, Edge, Workflow, Pattern)
│   ├── parser/parse.py        # n8n JSON -> Workflow objects
│   ├── patterns/analyzer.py   # Pattern extraction & similarity search
│   ├── translator/claude_code.py  # Pattern -> Claude Code architecture
│   └── mcp_server/server.py   # MCP server exposing all tools
├── tests/                     # 20 unit tests
├── evals/                     # 10 evaluation test cases
├── data/sample_workflows/     # Sample n8n workflow JSONs
├── .github/workflows/ci.yml   # CI pipeline (lint + test)
└── mcp.json                   # MCP server config for Claude Code
```

## Running Tests

```bash
uv run pytest -v          # Unit tests (20 tests)
uv run ruff check src/    # Linting
uv run python evals/run_evals.py  # Evaluation suite (10 cases)
```

## Data Source

Workflow data comes from [n8nworkflows.xyz](https://github.com/nusquama/n8nworkflows.xyz), an independent archive of 7,000+ public n8n workflow templates. The sample dataset includes 15 workflows for development; the full dataset can be loaded by cloning the source repository into `data/`.

## License

MIT
