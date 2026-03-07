"""MCP Server for Workflow Patterns.

Exposes workflow analysis tools to Claude:
- search_patterns: Find patterns matching a use case description
- analyze_workflow: Break down a workflow JSON into abstract components
- suggest_implementation: Get Claude Code architecture for a pattern
- list_categories: Show all known pattern categories with stats
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from workflow_patterns.models import Workflow
from workflow_patterns.parser.parse import parse_directory
from workflow_patterns.patterns.analyzer import (
    extract_common_pairs,
    extract_node_stats,
    extract_patterns,
    find_similar_workflows,
)
from workflow_patterns.translator.claude_code import translate_pattern

# Initialize MCP server
mcp = FastMCP(
    "workflow-patterns",
    instructions="Analyze automation workflow patterns and translate them to Claude Code architectures",
)

# Load workflows on startup — prefer full dataset, fall back to samples
_BASE_DIR = Path(__file__).parent.parent.parent.parent / "data"
DATA_DIR = (
    _BASE_DIR / "all_workflows"
    if (_BASE_DIR / "all_workflows").exists()
    else _BASE_DIR / "sample_workflows"
)
_workflows: list[Workflow] = []


def _ensure_loaded() -> list[Workflow]:
    """Lazy-load workflows on first use."""
    global _workflows
    if not _workflows and DATA_DIR.exists():
        _workflows = parse_directory(DATA_DIR)
    return _workflows


@mcp.tool()
def search_patterns(query: str) -> str:
    """Search for workflow patterns matching a use case description.

    Analyzes the query to identify relevant categories (trigger, ai, data,
    transform, deliver, api, logic, storage) and finds similar workflows.

    Args:
        query: Natural language description of what you want to automate.
               Example: "Send a weekly AI summary of news articles by email"
    """
    workflows = _ensure_loaded()
    if not workflows:
        return "No workflow data loaded. Check that data/sample_workflows/ contains workflow files."

    # Map query keywords to categories
    keyword_to_category = {
        "email": "deliver",
        "send": "deliver",
        "notify": "deliver",
        "slack": "deliver",
        "message": "deliver",
        "schedule": "trigger",
        "weekly": "trigger",
        "daily": "trigger",
        "when": "trigger",
        "watch": "trigger",
        "ai": "ai",
        "summarize": "ai",
        "analyze": "ai",
        "generate": "ai",
        "classify": "ai",
        "extract": "ai",
        "database": "data",
        "spreadsheet": "data",
        "sheet": "data",
        "csv": "data",
        "api": "api",
        "fetch": "api",
        "scrape": "api",
        "webhook": "trigger",
        "transform": "transform",
        "convert": "transform",
        "filter": "transform",
        "format": "transform",
        "file": "storage",
        "upload": "storage",
        "download": "storage",
        "drive": "storage",
        "condition": "logic",
        "if": "logic",
        "branch": "logic",
        "route": "logic",
    }

    query_lower = query.lower()
    matched_categories = []
    for keyword, category in keyword_to_category.items():
        if keyword in query_lower and category not in matched_categories:
            matched_categories.append(category)

    if not matched_categories:
        matched_categories = ["trigger", "ai"]  # reasonable default

    # Find similar workflows
    similar = find_similar_workflows(matched_categories, workflows, top_n=5)

    # Build response
    lines = [
        f"**Query:** {query}",
        f"**Detected categories:** {', '.join(matched_categories)}",
        "",
        "**Matching workflows:**",
    ]

    for wf, score in similar:
        lines.append(f"- [{score:.0%} match] **{wf.name}**")
        lines.append(f"  Pattern: `{wf.simple_signature}`")
        lines.append(f"  Nodes: {', '.join(n.type_short for n in wf.nodes[:6])}")
        if wf.source_url:
            lines.append(f"  Source: {wf.source_url}")
        lines.append("")

    # Also suggest a pattern
    suggested_pattern = " -> ".join(matched_categories)
    lines.append(f"**Suggested pattern:** `{suggested_pattern}`")
    lines.append("Use `suggest_implementation` with this pattern for Claude Code architecture.")

    return "\n".join(lines)


@mcp.tool()
def suggest_implementation(pattern: str) -> str:
    """Get a Claude Code architecture recommendation for a workflow pattern.

    Takes an abstract pattern signature and returns the components needed,
    implementation steps, and complexity assessment.

    Args:
        pattern: A pattern signature like 'trigger -> ai -> transform -> deliver'.
                 Valid categories: trigger, ai, transform, deliver, data, api, logic, storage.
    """
    arch = translate_pattern(pattern)
    return arch.to_text()


@mcp.tool()
def list_categories() -> str:
    """List all workflow categories with usage statistics.

    Shows how often each category appears across all analyzed workflows,
    plus the most common connections between categories.
    """
    workflows = _ensure_loaded()
    if not workflows:
        return "No workflow data loaded."

    stats = extract_node_stats(workflows)
    pairs = extract_common_pairs(workflows)

    lines = [
        f"**{len(workflows)} workflows analyzed**",
        "",
        "**Category frequency:**",
    ]

    for cat, count in stats.items():
        bar = "#" * min(count, 40)
        lines.append(f"  {cat:12s} {bar} ({count}x)")

    lines.append("")
    lines.append("**Most common connections:**")
    for src, tgt, count in pairs[:8]:
        lines.append(f"  {src} -> {tgt} ({count}x)")

    lines.append("")
    lines.append("**Available categories for patterns:**")
    lines.append("trigger, ai, transform, deliver, data, api, logic, storage")

    return "\n".join(lines)


@mcp.tool()
def show_all_patterns() -> str:
    """Show all unique workflow patterns found in the database, ranked by frequency.

    Returns simplified pattern signatures grouped by how often they appear.
    """
    workflows = _ensure_loaded()
    if not workflows:
        return "No workflow data loaded."

    patterns = extract_patterns(workflows, simplified=True)

    lines = [
        f"**{len(patterns)} unique patterns from {len(workflows)} workflows**",
        "",
    ]

    for p in patterns[:50]:
        lines.append(f"[{p.count}x] `{p.signature}`")
        for name in p.workflows[:3]:
            lines.append(f"     - {name}")
        if len(p.workflows) > 3:
            lines.append(f"     ... and {len(p.workflows) - 3} more")
        lines.append("")

    if len(patterns) > 50:
        lines.append(f"... and {len(patterns) - 50} more patterns (showing top 50)")

    return "\n".join(lines)
