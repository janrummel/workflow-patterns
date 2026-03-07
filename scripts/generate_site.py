"""Generate static GitHub Pages site from workflow analysis.

Analyzes all available workflows and produces docs/index.html
with interactive charts, use case clusters, and pattern statistics.

Usage:
    uv run python scripts/generate_site.py
"""

import json
from pathlib import Path

from workflow_patterns.parser.parse import parse_directory
from workflow_patterns.patterns.analyzer import (
    extract_common_pairs,
    extract_node_stats,
    extract_patterns,
)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "all_workflows"
if not DATA_DIR.exists():
    DATA_DIR = PROJECT_ROOT / "data" / "sample_workflows"
OUTPUT_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR.mkdir(exist_ok=True)


# --- Use case detection ---

USE_CASES = {
    "AI Chatbot / Assistant": {
        "icon": "🤖",
        "desc": "Conversational AI agents with memory, tools, and context awareness.",
        "example": "Customer support bot that answers questions using a knowledge base.",
        "check": lambda wf: (
            any(n.type_short in ("chatTrigger", "memoryBufferWindow", "agent") for n in wf.nodes)
            and any(n.category == "ai" for n in wf.nodes)
        ),
        "claude_code": "Claude agent + MCP servers for data access + CLAUDE.md for behavior",
    },
    "AI Content Creation": {
        "icon": "✍️",
        "desc": "Generate text, images, or media with AI and deliver via email, Slack, or CMS.",
        "example": "Weekly newsletter: fetch articles, summarize with AI, send by email.",
        "check": lambda wf: (
            any(n.category == "ai" for n in wf.nodes)
            and any(
                n.type_short
                in (
                    "openAi", "lmChatOpenAi", "lmChatGoogleGemini", "chainLlm",
                    "agent", "lmChatOpenRouter",
                )
                for n in wf.nodes
            )
            and any(
                n.type_short
                in ("wordpress", "gmail", "slack", "telegram", "discord", "emailSend")
                for n in wf.nodes
            )
        ),
        "claude_code": "Cron trigger + Claude agent for content + MCP server for delivery",
    },
    "Data Pipeline / ETL": {
        "icon": "🔄",
        "desc": "Move, transform, and sync data between databases, sheets, and APIs.",
        "example": "Sync new CRM contacts to Google Sheets every hour.",
        "check": lambda wf: (
            any(
                n.type_short
                in ("googleSheets", "postgres", "mysql", "airtable", "supabase", "notion", "mongo")
                for n in wf.nodes
            )
            and any(n.category == "transform" for n in wf.nodes)
            and not any(n.category == "ai" for n in wf.nodes)
        ),
        "claude_code": "Python script + MCP server for data sources + cron scheduler",
    },
    "Social Media Automation": {
        "icon": "📱",
        "desc": "Auto-post, monitor, or engage on social platforms with or without AI.",
        "example": "Generate LinkedIn posts from blog articles and schedule publishing.",
        "check": lambda wf: (
            any(
                n.type_short
                in (
                    "telegram", "telegramTrigger", "twitter", "linkedIn",
                    "reddit", "discord", "facebookGraphApi",
                )
                for n in wf.nodes
            )
            and any(n.category in ("ai", "transform") for n in wf.nodes)
        ),
        "claude_code": "Claude agent for content + MCP servers for each platform",
    },
    "Email Automation": {
        "icon": "📧",
        "desc": "Send, process, or route emails based on triggers and conditions.",
        "example": "When a form is submitted, send a confirmation email and notify the team.",
        "check": lambda wf: (
            any(
                n.type_short in ("gmail", "gmailTrigger", "emailSend", "microsoftOutlook")
                for n in wf.nodes
            )
            and any(
                n.type_short in ("scheduleTrigger", "cron", "webhook", "formTrigger")
                for n in wf.nodes
            )
        ),
        "claude_code": "MCP server for email + trigger script + optional Claude for personalization",
    },
    "Document Processing": {
        "icon": "📄",
        "desc": "Extract, transform, or analyze documents (PDF, images, files) with AI.",
        "example": "Extract invoice data from PDFs and write to a spreadsheet.",
        "check": lambda wf: (
            any(
                n.type_short
                in (
                    "extractFromFile", "convertToFile", "documentDefaultDataLoader",
                    "googleDocs", "googleDrive",
                )
                for n in wf.nodes
            )
            and any(n.category == "ai" for n in wf.nodes)
        ),
        "claude_code": "Claude agent with file tools + MCP server for storage",
    },
    "API Integration / Sync": {
        "icon": "🔗",
        "desc": "Connect external APIs, fetch data, and sync between services.",
        "example": "Pull data from a REST API, transform it, and store in a database.",
        "check": lambda wf: (
            any(n.type_short in ("httpRequest", "httpRequestTool") for n in wf.nodes)
            and any(
                n.type_short
                in ("googleSheets", "airtable", "notion", "supabase", "postgres")
                for n in wf.nodes
            )
            and not any(n.category == "ai" for n in wf.nodes)
        ),
        "claude_code": "MCP server wrapping the API + Python transform script + data MCP server",
    },
    "AI Data Analysis": {
        "icon": "📊",
        "desc": "Analyze data from databases or spreadsheets using AI for insights.",
        "example": "Analyze sales data weekly and generate a trend report.",
        "check": lambda wf: (
            any(n.category == "ai" for n in wf.nodes)
            and any(
                n.type_short in ("googleSheets", "postgres", "mysql", "airtable", "supabase")
                for n in wf.nodes
            )
            and not any(n.category == "deliver" for n in wf.nodes)
        ),
        "claude_code": "Claude agent + MCP server for data access + analysis skill",
    },
    "Lead Gen / CRM": {
        "icon": "🎯",
        "desc": "Capture, enrich, score, and route leads through a sales pipeline.",
        "example": "Enrich new leads with company data and assign to sales reps.",
        "check": lambda wf: (
            any(
                n.type_short in ("hubspot", "pipedrive", "salesforce", "pipedriveTool")
                for n in wf.nodes
            )
            or ("lead" in wf.name.lower() or "crm" in wf.name.lower())
        ),
        "claude_code": "MCP server for CRM + Claude agent for scoring + webhook trigger",
    },
    "Scheduled Notifications": {
        "icon": "🔔",
        "desc": "Send alerts, reminders, or digests on a schedule — no AI needed.",
        "example": "Every morning, check for overdue tasks and send a Slack reminder.",
        "check": lambda wf: (
            any(n.type_short in ("scheduleTrigger", "cron") for n in wf.nodes)
            and any(n.category == "deliver" for n in wf.nodes)
            and not any(n.category == "ai" for n in wf.nodes)
        ),
        "claude_code": "Cron job + Python script + MCP server for notifications",
    },
    "RAG / Knowledge Base": {
        "icon": "🧠",
        "desc": "Build AI systems that retrieve and reason over your own documents.",
        "example": "Upload docs to a vector store, then query with natural language.",
        "check": lambda wf: any(
            n.type_short
            in (
                "vectorStoreQdrant", "vectorStorePinecone", "vectorStoreSupabase",
                "embeddingsOpenAi", "documentDefaultDataLoader",
                "textSplitterRecursiveCharacterTextSplitter",
            )
            for n in wf.nodes
        ),
        "claude_code": "Claude agent + vector store MCP server + document ingestion script",
    },
    "Form / Webhook Handler": {
        "icon": "📥",
        "desc": "React to incoming HTTP requests or form submissions with processing logic.",
        "example": "Receive a webhook, validate the data, and update a database.",
        "check": lambda wf: (
            any(
                n.type_short in ("formTrigger", "webhook", "respondToWebhook")
                for n in wf.nodes
            )
            and not any(n.category == "ai" for n in wf.nodes)
        ),
        "claude_code": "Python webhook server + data validation script + MCP server for storage",
    },
}


def detect_use_cases(workflows):
    """Classify each workflow into use case clusters."""
    results = {}
    for name, uc in USE_CASES.items():
        matching = [wf for wf in workflows if uc["check"](wf)]
        avg_nodes = sum(len(wf.nodes) for wf in matching) / max(len(matching), 1)
        # Top pattern for this use case
        from collections import Counter

        sig_counter = Counter(wf.simple_signature for wf in matching)
        top_pattern = sig_counter.most_common(1)[0] if sig_counter else ("unknown", 0)
        results[name] = {
            "count": len(matching),
            "pct": len(matching) / len(workflows) * 100,
            "avg_nodes": avg_nodes,
            "top_pattern": top_pattern,
            "examples": matching[:3],
        }
    return results


def classify_complexity(workflows):
    """Group workflows by complexity tier."""
    tiers = {
        "Quick Automation": {"range": "2-3 nodes", "desc": "Simple one-step automations. Trigger something, do one action.", "wfs": []},
        "Standard Workflow": {"range": "4-6 nodes", "desc": "Common business processes with a few steps and some logic.", "wfs": []},
        "Medium Pipeline": {"range": "7-10 nodes", "desc": "Multi-step workflows with transforms, conditions, and integrations.", "wfs": []},
        "Complex System": {"range": "11-20 nodes", "desc": "Sophisticated automations combining AI, multiple data sources, and branching logic.", "wfs": []},
        "Enterprise Pipeline": {"range": "21+ nodes", "desc": "Large-scale workflows with many integrations, error handling, and parallel processing.", "wfs": []},
    }
    for wf in workflows:
        n = len(wf.nodes)
        if n <= 3:
            tiers["Quick Automation"]["wfs"].append(wf)
        elif n <= 6:
            tiers["Standard Workflow"]["wfs"].append(wf)
        elif n <= 10:
            tiers["Medium Pipeline"]["wfs"].append(wf)
        elif n <= 20:
            tiers["Complex System"]["wfs"].append(wf)
        else:
            tiers["Enterprise Pipeline"]["wfs"].append(wf)
    return tiers


def get_building_blocks(workflows):
    """Extract the most used concrete tools/nodes."""
    from collections import Counter

    counter = Counter()
    for wf in workflows:
        for n in wf.nodes:
            counter[n.type_short] += 1

    # Map tool names to human-readable descriptions
    tool_info = {
        "set": ("Set Fields", "transform", "Assign or rename data fields"),
        "code": ("Code (JavaScript/Python)", "transform", "Custom code for any transformation"),
        "httpRequest": ("HTTP Request", "api", "Call any REST API endpoint"),
        "if": ("If Condition", "logic", "Branch workflow based on conditions"),
        "agent": ("AI Agent", "ai", "Autonomous AI agent with tool access"),
        "googleSheets": ("Google Sheets", "data", "Read/write spreadsheet data"),
        "scheduleTrigger": ("Schedule Trigger", "trigger", "Run workflow on a schedule"),
        "lmChatOpenAi": ("OpenAI Chat", "ai", "GPT-4o / GPT-4 language model"),
        "manualTrigger": ("Manual Trigger", "trigger", "Start workflow with a button click"),
        "merge": ("Merge", "logic", "Combine data from multiple branches"),
        "gmail": ("Gmail", "deliver", "Send or read emails via Gmail"),
        "splitInBatches": ("Split In Batches", "logic", "Process items in smaller groups"),
        "outputParserStructured": ("Structured Output", "ai", "Parse AI output into structured data"),
        "webhook": ("Webhook", "trigger", "Receive HTTP requests as triggers"),
        "openAi": ("OpenAI", "ai", "Direct OpenAI API calls"),
        "switch": ("Switch", "logic", "Route to different paths by value"),
        "splitOut": ("Split Out", "transform", "Split arrays into individual items"),
        "telegram": ("Telegram", "deliver", "Send messages via Telegram"),
        "slack": ("Slack", "deliver", "Post messages to Slack channels"),
        "googleDrive": ("Google Drive", "storage", "Upload/download files from Drive"),
        "formTrigger": ("Form Trigger", "trigger", "Start workflow from a web form"),
        "aggregate": ("Aggregate", "transform", "Combine multiple items into one"),
        "memoryBufferWindow": ("Chat Memory", "ai", "Remember conversation history"),
        "lmChatGoogleGemini": ("Google Gemini", "ai", "Gemini language model"),
        "chainLlm": ("LLM Chain", "ai", "Chain multiple AI prompts together"),
        "filter": ("Filter", "transform", "Keep only items matching conditions"),
        "chatTrigger": ("Chat Trigger", "trigger", "Start workflow from a chat message"),
        "telegramTrigger": ("Telegram Trigger", "trigger", "React to Telegram messages"),
        "extractFromFile": ("Extract from File", "transform", "Read data from PDF, CSV, etc."),
        "emailSend": ("Email Send", "deliver", "Send email via SMTP"),
    }

    blocks = []
    for type_short, count in counter.most_common(30):
        info = tool_info.get(type_short, (type_short, "other", ""))
        blocks.append({
            "id": type_short,
            "name": info[0],
            "category": info[1],
            "desc": info[2],
            "count": count,
        })
    return blocks


def main():
    print(f"Loading workflows from {DATA_DIR.name}/ ...")
    workflows = parse_directory(DATA_DIR)
    print(f"  Parsed {len(workflows)} workflows")

    # Statistics
    node_stats = extract_node_stats(workflows)
    patterns = extract_patterns(workflows, simplified=True)
    pairs = extract_common_pairs(workflows)
    use_case_data = detect_use_cases(workflows)
    complexity_tiers = classify_complexity(workflows)
    building_blocks = get_building_blocks(workflows)

    # Prepare chart data
    cat_labels = [c for c in node_stats if c != "skip"]
    cat_values = [node_stats[c] for c in cat_labels]
    top_patterns = patterns[:25]

    html = build_html(
        total_workflows=len(workflows),
        total_patterns=len(patterns),
        total_nodes=sum(cat_values),
        cat_labels=cat_labels,
        cat_values=cat_values,
        top_patterns=top_patterns,
        pairs=pairs[:15],
        use_case_data=use_case_data,
        complexity_tiers=complexity_tiers,
        building_blocks=building_blocks,
    )

    output_path = OUTPUT_DIR / "index.html"
    output_path.write_text(html)
    print(f"  Site generated: {output_path}")


def build_html(
    total_workflows, total_patterns, total_nodes,
    cat_labels, cat_values, top_patterns, pairs,
    use_case_data, complexity_tiers, building_blocks,
):
    # --- Use case cards ---
    uc_cards = ""
    for name, uc_meta in USE_CASES.items():
        data = use_case_data[name]
        if data["count"] == 0:
            continue
        tp_sig, tp_count = data["top_pattern"]
        examples_html = ""
        for wf in data["examples"]:
            steps = " &rarr; ".join(
                f'<span class="step step-{s.strip()}">{s.strip()}</span>'
                for s in wf.simple_signature.split("->")
            )
            wf_name = wf.name[:60] + ("..." if len(wf.name) > 60 else "")
            examples_html += f'<div class="uc-example"><div class="uc-example-name">{wf_name}</div><div class="uc-example-steps">{steps}</div></div>'

        uc_cards += f"""
        <div class="uc-card">
            <div class="uc-header">
                <span class="uc-icon">{uc_meta['icon']}</span>
                <div>
                    <h3>{name}</h3>
                    <span class="uc-count">{data['count']:,} workflows ({data['pct']:.0f}%)</span>
                </div>
            </div>
            <p class="uc-desc">{uc_meta['desc']}</p>
            <div class="uc-detail">
                <div class="uc-detail-label">Typical example</div>
                <div class="uc-detail-value">{uc_meta['example']}</div>
            </div>
            <div class="uc-detail">
                <div class="uc-detail-label">Most common pattern</div>
                <div class="uc-detail-value"><code>{tp_sig}</code> ({tp_count}x)</div>
            </div>
            <div class="uc-detail">
                <div class="uc-detail-label">Avg. complexity</div>
                <div class="uc-detail-value">{data['avg_nodes']:.0f} nodes per workflow</div>
            </div>
            <div class="uc-detail">
                <div class="uc-detail-label">Claude Code approach</div>
                <div class="uc-detail-value claude-approach">{uc_meta['claude_code']}</div>
            </div>
            <div class="uc-examples-section">
                <div class="uc-detail-label">Real workflow examples</div>
                {examples_html}
            </div>
        </div>"""

    # --- Complexity tiers ---
    tier_cards = ""
    tier_labels = []
    tier_values = []
    for tier_name, tier_data in complexity_tiers.items():
        count = len(tier_data["wfs"])
        if count == 0:
            continue
        tier_labels.append(tier_name)
        tier_values.append(count)
        # Top 3 patterns for this tier
        from collections import Counter
        sig_counter = Counter(wf.simple_signature for wf in tier_data["wfs"])
        top3 = sig_counter.most_common(3)
        patterns_html = ""
        for sig, cnt in top3:
            steps = " &rarr; ".join(
                f'<span class="step step-{s.strip()}">{s.strip()}</span>'
                for s in sig.split("->")
            )
            patterns_html += f'<div class="tier-pattern">{steps} <span class="tier-count">{cnt}x</span></div>'

        tier_cards += f"""
        <div class="tier-card">
            <div class="tier-header">
                <h3>{tier_name}</h3>
                <span class="tier-range">{tier_data['range']}</span>
            </div>
            <div class="tier-count-big">{count:,}</div>
            <p class="tier-desc">{tier_data['desc']}</p>
            <div class="tier-patterns-label">Top patterns:</div>
            {patterns_html}
        </div>"""

    # --- Building blocks ---
    blocks_html = ""
    for b in building_blocks:
        bar_width = min(b["count"] // 15, 280)
        blocks_html += f"""
        <tr>
            <td><span class="block-name">{b['name']}</span></td>
            <td><span class="step step-{b['category']}">{b['category']}</span></td>
            <td class="block-desc">{b['desc']}</td>
            <td><div class="bar" style="width:{bar_width}px">{b['count']:,}</div></td>
        </tr>"""

    # --- Connection table ---
    conn_rows = ""
    for src, tgt, count in pairs:
        bar_width = min(count // 8, 250)
        conn_rows += (
            f'<tr><td><span class="step step-{src}">{src}</span></td>'
            f'<td><span class="step step-{tgt}">{tgt}</span></td>'
            f'<td><div class="bar" style="width:{bar_width}px">{count:,}</div></td></tr>'
        )

    # --- Top patterns with context ---
    pattern_cards = ""
    for p in top_patterns[:15]:
        steps_html = " &rarr; ".join(
            f'<span class="step step-{s.strip()}">{s.strip()}</span>'
            for s in p.signature.split("->")
        )
        examples = ", ".join(p.example_nodes[:6])
        pattern_cards += f"""
        <div class="pattern-card">
            <div class="pattern-sig">{steps_html}</div>
            <div class="pattern-meta">
                <span class="pattern-count">{p.count}x</span>
                <span class="pattern-examples">{examples}</span>
            </div>
        </div>"""

    # --- Chart data ---
    cat_labels_j = json.dumps(cat_labels)
    cat_values_j = json.dumps(cat_values)
    pat_labels_j = json.dumps([p.signature for p in top_patterns])
    pat_values_j = json.dumps([p.count for p in top_patterns])
    tier_labels_j = json.dumps(tier_labels)
    tier_values_j = json.dumps(tier_values)

    # Use case chart data
    uc_sorted = sorted(use_case_data.items(), key=lambda x: -x[1]["count"])
    uc_labels_j = json.dumps([name for name, _ in uc_sorted])
    uc_values_j = json.dumps([d["count"] for _, d in uc_sorted])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Workflow Patterns — {total_workflows:,} Automation Workflows Analyzed</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root {{
  --bg: #0d1117; --surface: #161b22; --surface2: #1c2129;
  --border: #30363d; --text: #e6edf3; --text-muted: #8b949e;
  --accent: #58a6ff; --green: #3fb950; --purple: #d2a8ff;
  --orange: #f78166; --cyan: #56d4dd; --yellow: #e3b341;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }}
.container {{ max-width:1200px; margin:0 auto; padding:2rem; }}
header {{ text-align:center; padding:3rem 0 1.5rem; border-bottom:1px solid var(--border); margin-bottom:2rem; }}
h1 {{ font-size:2.4rem; margin-bottom:0.3rem; }} h1 span {{ color:var(--accent); }}
.subtitle {{ color:var(--text-muted); font-size:1.05rem; max-width:700px; margin:0 auto; }}
nav {{ display:flex; flex-wrap:wrap; gap:0.5rem; justify-content:center; margin:1.5rem 0; }}
nav a {{ color:var(--accent); text-decoration:none; padding:6px 14px; border:1px solid var(--border); border-radius:16px; font-size:0.85rem; transition:all 0.2s; }}
nav a:hover {{ background:var(--accent); color:var(--bg); }}
.stats-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1.2rem; margin:1.5rem 0 2.5rem; }}
.stat-card {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.2rem; text-align:center; }}
.stat-number {{ font-size:2.2rem; font-weight:700; color:var(--accent); }}
.stat-label {{ color:var(--text-muted); font-size:0.9rem; }}
section {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:2rem; margin:2rem 0; }}
h2 {{ font-size:1.4rem; margin-bottom:0.3rem; padding-bottom:0.5rem; border-bottom:1px solid var(--border); }}
.section-desc {{ color:var(--text-muted); margin-bottom:1.5rem; font-size:0.95rem; }}
.chart-container {{ position:relative; height:350px; width:100%; }}
.chart-container-tall {{ position:relative; height:550px; width:100%; }}

/* Use case cards */
.uc-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(520px,1fr)); gap:1.5rem; }}
.uc-card {{ background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:1.5rem; }}
.uc-header {{ display:flex; align-items:center; gap:0.8rem; margin-bottom:0.8rem; }}
.uc-icon {{ font-size:1.8rem; }}
.uc-header h3 {{ font-size:1.1rem; margin:0; }}
.uc-count {{ color:var(--accent); font-size:0.85rem; font-weight:600; }}
.uc-desc {{ color:var(--text-muted); margin-bottom:1rem; font-size:0.9rem; }}
.uc-detail {{ margin:0.5rem 0; }}
.uc-detail-label {{ color:var(--text-muted); font-size:0.75rem; text-transform:uppercase; font-weight:600; letter-spacing:0.5px; }}
.uc-detail-value {{ font-size:0.9rem; }}
.claude-approach {{ color:var(--purple); font-style:italic; }}
.uc-examples-section {{ margin-top:0.8rem; }}
.uc-example {{ background:var(--surface2); border-radius:4px; padding:0.5rem 0.8rem; margin:0.4rem 0; }}
.uc-example-name {{ font-size:0.8rem; color:var(--text-muted); margin-bottom:0.2rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.uc-example-steps {{ font-size:0.85rem; }}

/* Complexity tiers */
.tier-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:1.2rem; }}
.tier-card {{ background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:1.2rem; text-align:center; }}
.tier-header h3 {{ font-size:1rem; margin:0; }}
.tier-range {{ color:var(--text-muted); font-size:0.8rem; }}
.tier-count-big {{ font-size:2rem; font-weight:700; color:var(--accent); margin:0.5rem 0; }}
.tier-desc {{ color:var(--text-muted); font-size:0.85rem; margin-bottom:0.8rem; }}
.tier-patterns-label {{ color:var(--text-muted); font-size:0.75rem; text-transform:uppercase; font-weight:600; margin-bottom:0.4rem; }}
.tier-pattern {{ margin:0.4rem 0; font-size:0.8rem; }}
.tier-count {{ color:var(--text-muted); font-size:0.75rem; }}

/* Building blocks table */
table {{ width:100%; border-collapse:collapse; }}
th,td {{ padding:0.5rem 0.8rem; text-align:left; border-bottom:1px solid var(--border); font-size:0.9rem; }}
th {{ color:var(--text-muted); font-weight:600; font-size:0.8rem; text-transform:uppercase; }}
.block-name {{ font-weight:600; }}
.block-desc {{ color:var(--text-muted); font-size:0.85rem; }}

/* Steps / badges */
.step {{ display:inline-block; padding:1px 8px; border-radius:10px; font-size:0.8rem; font-weight:600; }}
.step-trigger {{ background:#1f3a1f; color:#3fb950; }}
.step-ai {{ background:#2d1f3a; color:#d2a8ff; }}
.step-transform {{ background:#1f2d3a; color:#58a6ff; }}
.step-deliver {{ background:#3a2a1f; color:#f78166; }}
.step-data {{ background:#1f3a3a; color:#56d4dd; }}
.step-api {{ background:#3a3a1f; color:#e3b341; }}
.step-logic {{ background:#2a2a2a; color:#8b949e; }}
.step-storage {{ background:#1f2a2a; color:#79c0ff; }}
.step-other {{ background:#2a2a2a; color:#6e7681; }}

.bar {{
  background:linear-gradient(90deg,var(--accent),var(--purple));
  height:20px; border-radius:4px; color:white;
  font-size:0.75rem; padding:0 8px; display:flex; align-items:center; min-width:40px;
}}

/* Pattern cards */
.pattern-card {{ background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:0.8rem 1rem; margin:0.6rem 0; }}
.pattern-sig {{ margin-bottom:0.4rem; }}
.pattern-meta {{ display:flex; gap:0.8rem; align-items:center; }}
.pattern-count {{ background:var(--accent); color:var(--bg); font-weight:700; padding:1px 8px; border-radius:8px; font-size:0.75rem; }}
.pattern-examples {{ color:var(--text-muted); font-size:0.8rem; }}

.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:2rem; }}
@media (max-width:900px) {{
  .two-col {{ grid-template-columns:1fr; }}
  .uc-grid {{ grid-template-columns:1fr; }}
  .tier-grid {{ grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); }}
}}
footer {{ text-align:center; color:var(--text-muted); padding:2rem 0; font-size:0.85rem; border-top:1px solid var(--border); margin-top:2rem; }}
footer a {{ color:var(--accent); text-decoration:none; }}
code {{ background:var(--surface2); padding:2px 6px; border-radius:4px; font-size:0.85rem; }}
</style>
</head>
<body>
<div class="container">

<header>
  <h1>Workflow <span>Patterns</span></h1>
  <p class="subtitle">
    What do {total_workflows:,} real-world automation workflows have in common?
    This analysis extracts the universal patterns behind them — the building blocks,
    use cases, and architectures that power everyday automation.
  </p>
</header>

<nav>
  <a href="#use-cases">Use Cases</a>
  <a href="#complexity">Complexity</a>
  <a href="#building-blocks">Building Blocks</a>
  <a href="#categories">Categories</a>
  <a href="#patterns">Top Patterns</a>
  <a href="#connections">Connections</a>
</nav>

<div class="stats-grid">
  <div class="stat-card"><div class="stat-number">{total_workflows:,}</div><div class="stat-label">Workflows Analyzed</div></div>
  <div class="stat-card"><div class="stat-number">{total_nodes:,}</div><div class="stat-label">Total Nodes</div></div>
  <div class="stat-card"><div class="stat-number">{total_patterns:,}</div><div class="stat-label">Unique Patterns</div></div>
  <div class="stat-card"><div class="stat-number">{len(cat_labels)}</div><div class="stat-label">Categories</div></div>
  <div class="stat-card"><div class="stat-number">12</div><div class="stat-label">Use Case Clusters</div></div>
</div>

<!-- USE CASES -->
<section id="use-cases">
  <h2>What People Automate</h2>
  <p class="section-desc">
    Every workflow solves a real problem. We clustered {total_workflows:,} workflows into 12 use case
    families — from simple notification bots to complex AI pipelines.
    Each card shows how often this pattern appears, what it looks like, and how
    you could build it with Claude Code.
  </p>
  <div class="chart-container" style="margin-bottom:2rem;">
    <canvas id="ucChart"></canvas>
  </div>
  <div class="uc-grid">
    {uc_cards}
  </div>
</section>

<!-- COMPLEXITY -->
<section id="complexity">
  <h2>How Complex Are Real Workflows?</h2>
  <p class="section-desc">
    Not every automation needs 20 steps. Most real-world workflows range from
    4 to 20 nodes. Here's how they distribute — and the top patterns at each tier.
  </p>
  <div class="chart-container" style="margin-bottom:2rem;">
    <canvas id="tierChart"></canvas>
  </div>
  <div class="tier-grid">
    {tier_cards}
  </div>
</section>

<!-- BUILDING BLOCKS -->
<section id="building-blocks">
  <h2>The 30 Most-Used Building Blocks</h2>
  <p class="section-desc">
    These are the concrete tools that appear most often across all workflows.
    Each one maps to an abstract category (trigger, ai, transform, etc.).
  </p>
  <table>
    <thead><tr><th>Tool</th><th>Category</th><th>What it does</th><th>Usage</th></tr></thead>
    <tbody>{blocks_html}</tbody>
  </table>
</section>

<!-- CATEGORIES -->
<section id="categories">
  <h2>Abstract Categories</h2>
  <p class="section-desc">
    Every node type is mapped to one of {len(cat_labels)} abstract categories.
    This abstraction reveals the universal patterns behind different tool choices.
  </p>
  <div class="chart-container">
    <canvas id="catChart"></canvas>
  </div>
</section>

<!-- TOP PATTERNS -->
<section id="patterns">
  <h2>Top 15 Workflow Architectures</h2>
  <p class="section-desc">
    The most recurring sequences of categories — the "DNA" of automation.
    Read left to right: each step shows what kind of action happens at that point.
  </p>
  <div class="chart-container-tall" style="margin-bottom:1.5rem;">
    <canvas id="patChart"></canvas>
  </div>
  {pattern_cards}
</section>

<!-- CONNECTIONS -->
<section id="connections">
  <h2>How Categories Connect</h2>
  <p class="section-desc">
    Which categories feed into which? This shows the most frequent
    category-to-category edges across all workflows.
  </p>
  <table>
    <thead><tr><th>From</th><th>To</th><th>Frequency</th></tr></thead>
    <tbody>{conn_rows}</tbody>
  </table>
</section>

<footer>
  <p>
    Built with <a href="https://github.com/janrummel/workflow-patterns">workflow-patterns</a>
    &middot; Data: <a href="https://github.com/nusquama/n8nworkflows.xyz">n8nworkflows.xyz</a>
    &middot; Powered by Claude Code
  </p>
</footer>

</div>

<script>
const catColors = {{
  trigger:'#3fb950', ai:'#d2a8ff', transform:'#58a6ff',
  deliver:'#f78166', data:'#56d4dd', api:'#e3b341',
  logic:'#8b949e', storage:'#79c0ff', other:'#484f58'
}};

// Use case chart
new Chart(document.getElementById('ucChart'), {{
  type:'bar',
  data:{{
    labels:{uc_labels_j},
    datasets:[{{ data:{uc_values_j}, backgroundColor:'#58a6ff', borderRadius:4 }}]
  }},
  options:{{
    indexAxis:'y', responsive:true, maintainAspectRatio:false,
    plugins:{{ legend:{{display:false}}, tooltip:{{ callbacks:{{ label:c=>c.parsed.x.toLocaleString()+' workflows' }} }} }},
    scales:{{
      x:{{ ticks:{{color:'#8b949e'}}, grid:{{color:'#30363d'}} }},
      y:{{ ticks:{{color:'#e6edf3',font:{{size:12}}}}, grid:{{display:false}} }}
    }}
  }}
}});

// Complexity tier chart
new Chart(document.getElementById('tierChart'), {{
  type:'doughnut',
  data:{{
    labels:{tier_labels_j},
    datasets:[{{ data:{tier_values_j}, backgroundColor:['#3fb950','#58a6ff','#e3b341','#f78166','#d2a8ff'], borderWidth:0 }}]
  }},
  options:{{
    responsive:true, maintainAspectRatio:false,
    plugins:{{
      legend:{{ position:'right', labels:{{color:'#e6edf3',padding:16,font:{{size:13}}}} }},
      tooltip:{{ callbacks:{{ label:c=>c.label+': '+c.parsed.toLocaleString()+' workflows' }} }}
    }}
  }}
}});

// Category chart
new Chart(document.getElementById('catChart'), {{
  type:'bar',
  data:{{
    labels:{cat_labels_j},
    datasets:[{{ data:{cat_values_j}, backgroundColor:{cat_labels_j}.map(l=>catColors[l]||'#484f58'), borderRadius:4 }}]
  }},
  options:{{
    indexAxis:'y', responsive:true, maintainAspectRatio:false,
    plugins:{{ legend:{{display:false}}, tooltip:{{ callbacks:{{ label:c=>c.parsed.x.toLocaleString()+' nodes' }} }} }},
    scales:{{
      x:{{ ticks:{{color:'#8b949e',callback:v=>v.toLocaleString()}}, grid:{{color:'#30363d'}} }},
      y:{{ ticks:{{color:'#e6edf3',font:{{size:14,weight:'bold'}}}}, grid:{{display:false}} }}
    }}
  }}
}});

// Pattern chart
new Chart(document.getElementById('patChart'), {{
  type:'bar',
  data:{{
    labels:{pat_labels_j},
    datasets:[{{ data:{pat_values_j}, backgroundColor:'#58a6ff', borderRadius:3 }}]
  }},
  options:{{
    indexAxis:'y', responsive:true, maintainAspectRatio:false,
    plugins:{{ legend:{{display:false}}, tooltip:{{ callbacks:{{ label:c=>c.parsed.x+' workflows' }} }} }},
    scales:{{
      x:{{ ticks:{{color:'#8b949e'}}, grid:{{color:'#30363d'}} }},
      y:{{ ticks:{{color:'#e6edf3',font:{{size:11}}}}, grid:{{display:false}} }}
    }}
  }}
}});
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()
