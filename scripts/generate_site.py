"""Generate static GitHub Pages site from workflow analysis.

Analyzes all available workflows and produces docs/index.html
with interactive charts, use case clusters, and pattern statistics.

Usage:
    uv run python scripts/generate_site.py
"""

import json
from collections import Counter
from pathlib import Path

from workflow_patterns.parser.parse import parse_directory
from workflow_patterns.patterns.analyzer import extract_patterns

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
    for type_short, count in counter.most_common(20):
        info = tool_info.get(type_short, (type_short, "other", ""))
        blocks.append({
            "id": type_short,
            "name": info[0],
            "category": info[1],
            "desc": info[2],
            "count": count,
        })
    return blocks


WIZARD_DATA = {
    "AI Chatbot / Assistant": {
        "question": "People keep asking me the same questions",
        "pattern": "trigger -> ai -> data -> deliver",
        "tools": ["Chat Trigger", "Claude Agent", "Memory Buffer", "Data Source (MCP)"],
        "apps": [
            ("OpenAI GPT-4", "ai", 2854), ("Google Gemini", "ai", 1068),
            ("Google Sheets", "data", 2105), ("Telegram", "deliver", 1279),
            ("Gmail", "deliver", 1008), ("Slack", "deliver", 490),
            ("Pinecone", "storage", 208), ("Supabase", "data", 180),
        ],
        "code": """from anthropic import Anthropic

client = Anthropic()
conversation = []

def chat(user_message):
    conversation.append({"role": "user", "content": user_message})
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a helpful assistant. Answer based on the knowledge base.",
        messages=conversation,
    )
    reply = response.content[0].text
    conversation.append({"role": "assistant", "content": reply})
    return reply""",
        "run": "python chatbot.py  # or expose as MCP server",
        "learn": ["Claude API basics", "Conversation memory", "System prompts", "MCP tool design"],
        "example": {
            "path": "examples/ai-chatbot",
            "label": "Runnable Example",
            "desc": "22 tests, Claude API streaming, 5 personas, conversation memory — ready to run",
        },
    },
    "AI Content Creation": {
        "question": "I regularly write similar content (newsletters, posts, summaries)",
        "pattern": "trigger -> api -> ai -> deliver",
        "tools": ["Schedule/Cron", "HTTP Request", "Claude API", "Email/Slack"],
        "apps": [
            ("OpenAI GPT-4", "ai", 1632), ("Telegram", "deliver", 1712),
            ("Gmail", "deliver", 1686), ("Google Sheets", "data", 1848),
            ("WordPress", "api", 220), ("Slack", "deliver", 380),
            ("Discord", "deliver", 150), ("OpenRouter", "ai", 350),
        ],
        "code": """import anthropic, requests, smtplib
from email.message import EmailMessage

# 1. Fetch content
articles = requests.get("https://api.example.com/articles?days=7").json()

# 2. Summarize with Claude
client = anthropic.Anthropic()
summary = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": f"Summarize these articles:\\n{articles}"}],
).content[0].text

# 3. Send digest
msg = EmailMessage()
msg["Subject"] = "Your Weekly Digest"
msg.set_content(summary)
# ... send via SMTP""",
        "run": "cd examples/ai-content-creation && uv sync && uv run python run.py",
        "learn": ["RSS/Atom feed parsing", "Claude for summarization", "Markdown generation", "Modular workflow design"],
        "example": {
            "path": "examples/ai-content-creation",
            "label": "Runnable Example",
            "desc": "30 tests, Claude API, 60 curated feeds, interactive selection — ready to run",
        },
    },
    "Data Pipeline / ETL": {
        "question": "I copy data from A to B, always the same way",
        "pattern": "trigger -> data -> transform -> data",
        "tools": ["Schedule/Cron", "Database/Sheets Reader", "Python Transform", "Database Writer"],
        "apps": [
            ("Google Sheets", "data", 1965), ("Airtable", "data", 302),
            ("Gmail", "deliver", 348), ("PostgreSQL", "data", 120),
            ("MySQL", "data", 85), ("Notion", "data", 110),
            ("Supabase", "data", 95), ("MongoDB", "data", 45),
        ],
        "code": """import csv, sqlite3

# 1. Read source (CSV, API, database...)
with open("input.csv") as f:
    rows = list(csv.DictReader(f))

# 2. Transform
cleaned = [
    {"name": r["name"].strip(), "value": float(r["amount"])}
    for r in rows if r["amount"]
]

# 3. Write to destination
db = sqlite3.connect("output.db")
db.executemany("INSERT INTO records (name, value) VALUES (?, ?)",
    [(r["name"], r["value"]) for r in cleaned])
db.commit()""",
        "run": "crontab: 0 * * * * python sync_data.py",
        "learn": ["File I/O", "Data transformation", "Database basics", "Scheduled jobs"],
    },
    "Social Media Automation": {
        "question": "I post regularly on social platforms, always similar steps",
        "pattern": "trigger -> ai -> transform -> api",
        "tools": ["Schedule/Cron", "Claude API", "Text Formatter", "Platform API"],
        "apps": [
            ("Telegram", "deliver", 2504), ("OpenAI GPT-4", "ai", 681),
            ("Google Sheets", "data", 1091), ("Facebook/Instagram", "api", 280),
            ("LinkedIn", "api", 130), ("Twitter/X", "api", 113),
            ("Reddit", "api", 117), ("Discord", "deliver", 160),
        ],
        "code": """import anthropic, requests

# 1. Generate post with Claude
client = anthropic.Anthropic()
post = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Write a LinkedIn post about AI automation trends. Professional tone, 150 words max."}],
).content[0].text

# 2. Post to platform (e.g., via API)
requests.post("https://api.linkedin.com/v2/posts", json={
    "content": post,
}, headers={"Authorization": "Bearer YOUR_TOKEN"})""",
        "run": "crontab: 0 9 * * 2,4 python post_social.py",
        "learn": ["Claude for content generation", "OAuth APIs", "Prompt engineering", "Rate limiting"],
    },
    "Email Automation": {
        "question": "I write the same emails over and over",
        "pattern": "trigger -> transform -> deliver",
        "tools": ["Webhook/Form", "Template Engine", "SMTP / Gmail API"],
        "apps": [
            ("Gmail", "deliver", 1426), ("Google Sheets", "data", 1286),
            ("SMTP Email", "deliver", 509), ("OpenAI GPT-4", "ai", 649),
            ("Slack", "deliver", 180), ("Outlook", "deliver", 95),
            ("Airtable", "data", 120), ("Webhook", "trigger", 200),
        ],
        "code": """from email.message import EmailMessage
import smtplib

def send_confirmation(name, email, event):
    msg = EmailMessage()
    msg["To"] = email
    msg["Subject"] = f"Confirmed: {event}"
    msg.set_content(f\"\"\"Hi {name},

You're confirmed for {event}. See you there!
\"\"\")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login("you@gmail.com", "app-password")
        s.send_message(msg)""",
        "run": "python email_handler.py  # triggered by webhook or form",
        "learn": ["SMTP basics", "Email templating", "Webhook handling", "App passwords"],
    },
    "Document Processing": {
        "question": "I read documents and extract information from them",
        "pattern": "trigger -> storage -> ai -> data",
        "tools": ["File Watcher", "PDF/Doc Reader", "Claude API", "Spreadsheet/DB"],
        "apps": [
            ("Google Drive", "storage", 1211), ("Google Sheets", "data", 1053),
            ("OpenAI GPT-4", "ai", 940), ("Telegram", "deliver", 544),
            ("Google Docs", "storage", 180), ("PDF Extract", "transform", 547),
            ("Google Gemini", "ai", 320), ("Slack", "deliver", 150),
        ],
        "code": """import anthropic
from pathlib import Path

# 1. Read document
pdf_text = extract_text_from_pdf(Path("invoice.pdf"))

# 2. Extract structured data with Claude
client = anthropic.Anthropic()
result = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": f\"\"\"Extract from this invoice:
- Invoice number, date, total amount, vendor name
Return as JSON.

{pdf_text}\"\"\"}],
).content[0].text

# 3. Save to spreadsheet or database
save_to_sheets(json.loads(result))""",
        "run": "python process_docs.py invoices/",
        "learn": ["PDF parsing", "Claude for extraction", "Structured outputs", "File processing"],
    },
    "API Integration / Sync": {
        "question": "Two tools don't talk to each other",
        "pattern": "trigger -> api -> transform -> data",
        "tools": ["Schedule/Webhook", "HTTP Client", "Data Mapper", "Database/Sheets"],
        "apps": [
            ("Google Sheets", "data", 1290), ("Airtable", "data", 204),
            ("Notion", "data", 95), ("Supabase", "data", 80),
            ("PostgreSQL", "data", 75), ("Slack", "deliver", 85),
            ("Gmail", "deliver", 110), ("Webhook", "trigger", 163),
        ],
        "code": """import requests, json

# 1. Fetch from source API
response = requests.get("https://api.source.com/items",
    headers={"Authorization": "Bearer TOKEN_A"})
items = response.json()["data"]

# 2. Transform to target format
mapped = [{"name": i["title"], "status": i["state"]} for i in items]

# 3. Push to destination API
for item in mapped:
    requests.post("https://api.target.com/records",
        json=item, headers={"Authorization": "Bearer TOKEN_B"})""",
        "run": "crontab: */30 * * * * python sync_apis.py",
        "learn": ["REST APIs", "Authentication", "Data mapping", "Error handling"],
    },
    "AI Data Analysis": {
        "question": "I look at data and draw the same kind of conclusions",
        "pattern": "trigger -> data -> ai -> deliver",
        "tools": ["Schedule/Cron", "Database Query", "Claude API", "Report Delivery"],
        "apps": [
            ("Google Sheets", "data", 1425), ("OpenAI GPT-4", "ai", 509),
            ("Airtable", "data", 397), ("Google Drive", "storage", 324),
            ("PostgreSQL", "data", 95), ("Supabase", "data", 85),
            ("Google Gemini", "ai", 180), ("Notion", "data", 90),
        ],
        "code": """import anthropic, sqlite3

# 1. Query data
db = sqlite3.connect("sales.db")
rows = db.execute(\"\"\"
    SELECT product, SUM(revenue), COUNT(*)
    FROM sales WHERE date > date('now', '-7 days')
    GROUP BY product ORDER BY SUM(revenue) DESC
\"\"\").fetchall()

# 2. Analyze with Claude
client = anthropic.Anthropic()
analysis = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": f"Analyze this weekly sales data and highlight trends:\\n{rows}"}],
).content[0].text

# 3. Send report
send_slack_message("#reports", analysis)""",
        "run": "crontab: 0 8 * * 1 python weekly_analysis.py",
        "learn": ["SQL queries", "Claude for analysis", "Data visualization", "Report delivery"],
    },
    "Lead Gen / CRM": {
        "question": "I manage contacts and leads manually",
        "pattern": "trigger -> api -> ai -> data",
        "tools": ["Webhook", "Enrichment API", "Claude Scoring", "CRM Database"],
        "apps": [
            ("Google Sheets", "data", 560), ("HubSpot", "data", 203),
            ("Gmail", "deliver", 230), ("Airtable", "data", 207),
            ("OpenAI GPT-4", "ai", 205), ("Pipedrive", "data", 84),
            ("Salesforce", "data", 50), ("Slack", "deliver", 85),
        ],
        "code": """import anthropic, requests

def process_lead(lead):
    # 1. Enrich with company data
    company = requests.get(f"https://api.clearbit.com/v2/companies/find?domain={lead['domain']}").json()

    # 2. Score with Claude
    client = anthropic.Anthropic()
    score = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": f"Score this lead 1-10: {lead} Company: {company}"}],
    ).content[0].text

    # 3. Save to CRM
    save_to_crm({**lead, "company": company["name"], "score": score})""",
        "run": "python lead_handler.py  # triggered by webhook",
        "learn": ["Enrichment APIs", "AI scoring", "CRM integration", "Webhook handlers"],
    },
    "Scheduled Notifications": {
        "question": "I keep forgetting to check things",
        "pattern": "trigger -> api -> logic -> deliver",
        "tools": ["Cron Job", "HTTP Request", "Condition Check", "Slack/Email"],
        "apps": [
            ("Google Sheets", "data", 591), ("Gmail", "deliver", 315),
            ("Slack", "deliver", 271), ("Telegram", "deliver", 196),
            ("SMTP Email", "deliver", 177), ("Airtable", "data", 80),
            ("Notion", "data", 55), ("Discord", "deliver", 45),
        ],
        "code": """import requests

# 1. Check something
response = requests.get("https://api.example.com/status")
data = response.json()

# 2. Decide if notification needed
if data["items_overdue"] > 0:
    # 3. Send alert
    requests.post("https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        json={"text": f"Alert: {data['items_overdue']} overdue items!"})""",
        "run": "crontab: 0 9 * * * python check_and_notify.py",
        "learn": ["Cron basics", "REST APIs", "Conditional logic", "Slack webhooks"],
    },
    "RAG / Knowledge Base": {
        "question": "I'm always searching through my own documents",
        "pattern": "trigger -> storage -> ai -> data",
        "tools": ["Document Loader", "Embeddings", "Vector Store", "Claude Agent"],
        "apps": [
            ("OpenAI Embeddings", "ai", 428), ("Pinecone", "storage", 208),
            ("OpenAI GPT-4", "ai", 374), ("Google Drive", "storage", 215),
            ("Qdrant", "storage", 120), ("Supabase", "data", 95),
            ("Google Gemini", "ai", 80), ("PostgreSQL (pgvector)", "data", 45),
        ],
        "code": """# Ingest phase: run once
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")
db = chromadb.Client()
collection = db.create_collection("docs")

for doc in load_documents("./docs/"):
    embedding = model.encode(doc.text)
    collection.add(documents=[doc.text], embeddings=[embedding], ids=[doc.id])

# Query phase: run per question
def ask(question):
    results = collection.query(query_texts=[question], n_results=3)
    context = "\\n".join(results["documents"][0])
    # Use Claude with retrieved context
    return claude_answer(question, context)""",
        "run": "python ingest.py && python query.py 'What is our refund policy?'",
        "learn": ["Embeddings", "Vector databases", "RAG architecture", "Claude with context"],
    },
    "Form / Webhook Handler": {
        "question": "When something arrives, I have to process it manually",
        "pattern": "trigger -> transform -> logic -> data",
        "tools": ["Webhook Server", "Data Validator", "Router", "Database"],
        "apps": [
            ("Google Sheets", "data", 553), ("Slack", "deliver", 210),
            ("Gmail", "deliver", 196), ("Airtable", "data", 85),
            ("Notion", "data", 70), ("Telegram", "deliver", 65),
            ("PostgreSQL", "data", 40), ("Discord", "deliver", 35),
        ],
        "code": """from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))

        # Validate
        if not data.get("email") or not data.get("name"):
            self.send_response(400)
            return

        # Process and store
        save_to_database(data)
        self.send_response(200)

HTTPServer(("", 8080), WebhookHandler).serve_forever()""",
        "run": "python webhook_server.py  # listens on port 8080",
        "learn": ["HTTP servers", "JSON parsing", "Data validation", "Request handling"],
    },
}


def main():
    print(f"Loading workflows from {DATA_DIR.name}/ ...")
    workflows = parse_directory(DATA_DIR)
    print(f"  Parsed {len(workflows)} workflows")

    # Statistics
    patterns = extract_patterns(workflows, simplified=True)
    use_case_data = detect_use_cases(workflows)
    building_blocks = get_building_blocks(workflows)

    html = build_html(
        total_workflows=len(workflows),
        total_patterns=len(patterns),
        top_patterns=patterns[:10],
        use_case_data=use_case_data,
        building_blocks=building_blocks,
    )

    output_path = OUTPUT_DIR / "index.html"
    output_path.write_text(html)
    print(f"  Site generated: {output_path}")


def build_html(
    total_workflows, total_patterns,
    top_patterns, use_case_data, building_blocks,
):
    # --- Wizard data (baked into HTML as JSON) ---
    wizard_items = []
    for name, uc_meta in USE_CASES.items():
        wiz = WIZARD_DATA.get(name)
        if not wiz:
            continue
        data = use_case_data.get(name, {})
        wizard_items.append({
            "name": name,
            "icon": uc_meta["icon"],
            "question": wiz["question"],
            "desc": uc_meta["desc"],
            "pattern": wiz["pattern"],
            "tools": wiz["tools"],
            "apps": [{"name": a[0], "cat": a[1], "count": a[2]} for a in wiz.get("apps", [])],
            "code": wiz["code"],
            "run": wiz["run"],
            "learn": wiz["learn"],
            "claude_code": uc_meta["claude_code"],
            "count": data.get("count", 0),
            "pct": data.get("pct", 0),
            "avg_nodes": data.get("avg_nodes", 0),
            "example": wiz.get("example"),
        })
    wizard_json = json.dumps(wizard_items, indent=2)

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

    # --- Top patterns ---
    pattern_cards = ""
    for p in top_patterns[:10]:
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
    pat_labels_j = json.dumps([p.signature for p in top_patterns])
    pat_values_j = json.dumps([p.count for p in top_patterns])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Workflow Patterns — {total_workflows:,} Automation Workflows Analyzed</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1/themes/prism-tomorrow.min.css">
<script src="https://cdn.jsdelivr.net/npm/prismjs@1/prism.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-python.min.js"></script>
<style>
:root {{
  --bg: #0d1117; --surface: #161b22; --surface2: #1c2129;
  --border: #30363d; --text: #e6edf3; --text-muted: #8b949e;
  --accent: #58a6ff; --green: #3fb950; --purple: #d2a8ff;
  --orange: #f78166; --cyan: #56d4dd; --yellow: #e3b341;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }}
.container {{ max-width:1200px; margin:0 auto; padding:2rem; }}
header {{ text-align:center; padding:3rem 0 1.5rem; border-bottom:1px solid var(--border); margin-bottom:2rem; }}
h1 {{ font-size:2.4rem; margin-bottom:0.3rem; }} h1 span {{ color:var(--accent); }}
.subtitle {{ color:var(--text-muted); font-size:1.05rem; max-width:700px; margin:0 auto; }}
nav {{ display:flex; flex-wrap:wrap; gap:0.5rem; justify-content:center; margin:1.5rem 0; }}
nav a {{ color:var(--accent); text-decoration:none; padding:6px 14px; border:1px solid var(--border); border-radius:16px; font-size:0.85rem; transition:all 0.2s; }}
nav a:hover {{ background:var(--accent); color:var(--bg); }}
.stats-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:1.2rem; margin:1.5rem 0 2.5rem; }}
.stat-card {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.2rem; text-align:center; }}
.stat-number {{ font-size:2.2rem; font-weight:700; color:var(--accent); }}
.stat-label {{ color:var(--text-muted); font-size:0.9rem; }}
section {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:2rem; margin:2rem 0; }}
h2 {{ font-size:1.4rem; margin-bottom:0.3rem; padding-bottom:0.5rem; border-bottom:1px solid var(--border); }}
.section-desc {{ color:var(--text-muted); margin-bottom:1.5rem; font-size:0.95rem; }}
.chart-container {{ position:relative; height:350px; width:100%; }}

/* Steps / category badges */
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

/* Building blocks table */
table {{ width:100%; border-collapse:collapse; }}
th,td {{ padding:0.5rem 0.8rem; text-align:left; border-bottom:1px solid var(--border); font-size:0.9rem; }}
th {{ color:var(--text-muted); font-weight:600; font-size:0.8rem; text-transform:uppercase; }}
.block-name {{ font-weight:600; }}
.block-desc {{ color:var(--text-muted); font-size:0.85rem; }}

/* Pattern cards */
.pattern-card {{ background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:0.8rem 1rem; margin:0.6rem 0; }}
.pattern-sig {{ margin-bottom:0.4rem; }}
.pattern-meta {{ display:flex; gap:0.8rem; align-items:center; }}
.pattern-count {{ background:var(--accent); color:var(--bg); font-weight:700; padding:1px 8px; border-radius:8px; font-size:0.75rem; }}
.pattern-examples {{ color:var(--text-muted); font-size:0.8rem; }}

footer {{ text-align:center; color:var(--text-muted); padding:2rem 0; font-size:0.85rem; border-top:1px solid var(--border); margin-top:2rem; }}
footer a {{ color:var(--accent); text-decoration:none; }}
code {{ background:var(--surface2); padding:2px 6px; border-radius:4px; font-size:0.85rem; }}

/* Wizard */
.wizard-section {{ border:2px solid var(--accent); }}
.wizard-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; }}
.wizard-card {{
  background:var(--bg); border:1px solid var(--border); border-radius:8px;
  padding:1.2rem; cursor:pointer; transition:all 0.2s;
}}
.wizard-card:hover {{ border-color:var(--accent); transform:translateY(-2px); }}
.wizard-card-icon {{ font-size:1.5rem; margin-bottom:0.3rem; }}
.wizard-card h4 {{ font-size:0.95rem; margin:0.3rem 0; }}
.wizard-card p {{ color:var(--text-muted); font-size:0.85rem; margin:0; font-style:italic; }}
.wizard-card .wizard-card-count {{ color:var(--accent); font-size:0.75rem; margin-top:0.4rem; }}
.wizard-back {{
  background:none; border:1px solid var(--border); color:var(--accent);
  padding:6px 16px; border-radius:6px; cursor:pointer; margin-bottom:1.5rem;
  font-size:0.9rem; transition:all 0.2s;
}}
.wizard-back:hover {{ background:var(--accent); color:var(--bg); }}
/* Wizard result — card grid */
.wizard-result-header {{ display:flex; align-items:center; gap:0.8rem; margin-bottom:1.2rem; }}
.wizard-result-header h3 {{ margin:0; font-size:1.3rem; }}
.uc-icon {{ font-size:1.8rem; }}
.uc-count {{ color:var(--accent); font-size:0.85rem; font-weight:600; }}
.uc-desc {{ color:var(--text-muted); margin-bottom:1.2rem; font-size:0.9rem; }}
.wiz-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem; }}
.wiz-card {{ background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:1.2rem; }}
.wiz-card-full {{ grid-column:1/-1; }}
.wiz-card-title {{ color:var(--text-muted); font-size:0.7rem; text-transform:uppercase; font-weight:700; letter-spacing:0.8px; margin-bottom:0.6rem; }}
.wiz-card-title:not(:first-child) {{ margin-top:1.2rem; }}
.wiz-pattern-display {{ font-size:1.05rem; padding:0.3rem 0; }}
.wiz-tools-list {{ list-style:none; padding:0; }}
.wiz-tools-list li {{ padding:2px 0; font-size:0.9rem; }}
.wiz-tools-list li::before {{ content:"\\2022 "; color:var(--accent); font-weight:bold; }}
.wiz-learn-list {{ list-style:none; padding:0; }}
.wiz-learn-list li {{ padding:2px 0; font-size:0.85rem; color:var(--text-muted); }}
.wiz-learn-list li::before {{ content:"\\2713 "; color:var(--green); }}
.claude-approach {{ color:var(--purple); font-style:italic; font-size:0.9rem; }}
.wiz-run {{ display:block; padding:8px 12px; margin-top:4px; font-size:0.85rem; word-break:break-all; }}
.copy-btn {{
  background:var(--accent); color:var(--bg); border:none; border-radius:4px;
  padding:2px 10px; font-size:0.7rem; font-weight:600; cursor:pointer;
  margin-left:8px; vertical-align:middle;
}}
.copy-btn:hover {{ opacity:0.8; }}
/* Apps grouped by category */
.wiz-app-group {{ display:flex; align-items:baseline; gap:0.6rem; padding:0.4rem 0; border-bottom:1px solid var(--border); }}
.wiz-app-group:last-child {{ border-bottom:none; }}
.wiz-app-group-label {{ min-width:80px; flex-shrink:0; }}
.wiz-app-group-items {{ display:flex; flex-wrap:wrap; gap:6px; }}
.wiz-app-item {{ font-size:0.85rem; padding:2px 0; }}
.wiz-app-item::after {{ content:" · "; color:var(--border); }}
.wiz-app-item:last-child::after {{ content:""; }}
.wiz-app-count {{ color:var(--text-muted); font-size:0.7rem; }}
.wiz-example-link {{
  display:block; padding:10px 14px; border:2px solid var(--green); border-radius:8px;
  color:var(--green); text-decoration:none; font-weight:600; font-size:0.9rem;
  transition:all 0.2s; text-align:center;
}}
.wiz-example-link:hover {{ background:var(--green); color:var(--bg); }}
.wiz-code {{
  background:#1e1e2e !important; border:1px solid var(--border); border-radius:6px;
  padding:1rem; font-size:0.8rem; line-height:1.5; overflow-x:auto;
  white-space:pre; font-family:'SF Mono',SFMono-Regular,Consolas,monospace;
  max-height:400px; overflow-y:auto; margin-top:4px;
}}
.wiz-code code {{ background:transparent !important; font-size:0.8rem; }}
@media (max-width:700px) {{ .wiz-grid {{ grid-template-columns:1fr; }} }}
@media (max-width:900px) {{
  .stats-grid {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>
<div class="container">

<header>
  <h1>Workflow <span>Patterns</span></h1>
  <p class="subtitle">
    We analyzed {total_workflows:,} real n8n automation workflows and mapped every node
    to an abstract category (trigger, AI, transform, deliver, &hellip;). The result:
    universal patterns that show how people actually build automations &mdash;
    and how you can build yours.
  </p>
</header>

<nav>
  <a href="#wizard">Build a Workflow</a>
  <a href="#patterns">Patterns</a>
  <a href="#building-blocks">Tools</a>
</nav>

<!-- WIZARD -->
<section id="wizard" class="wizard-section">
  <h2>What Do You Want to Automate?</h2>
  <p class="section-desc">Pick a use case below. Get the pattern, the tools, and starter code &mdash; all based on {total_workflows:,} real workflows.</p>

  <div id="wizard-step1">
    <div class="wizard-grid" id="wizard-cards"></div>
  </div>

  <div id="wizard-step2" style="display:none;">
    <button class="wizard-back" onclick="wizardBack()">&larr; Pick a different use case</button>
    <div class="wizard-result">
      <div class="wizard-result-header">
        <span id="wiz-icon" class="uc-icon"></span>
        <div>
          <h3 id="wiz-name"></h3>
          <span id="wiz-stats" class="uc-count"></span>
        </div>
      </div>
      <p id="wiz-desc" class="uc-desc"></p>

      <div class="wiz-grid">
        <div class="wiz-card">
          <div class="wiz-card-title">Pattern</div>
          <div id="wiz-pattern" class="wiz-pattern-display"></div>
          <div class="wiz-card-title">Building Blocks</div>
          <ul id="wiz-tools" class="wiz-tools-list"></ul>
        </div>
        <div class="wiz-card">
          <div class="wiz-card-title">Claude Code Architecture</div>
          <p id="wiz-claude" class="claude-approach"></p>
          <div class="wiz-card-title">Run It</div>
          <code id="wiz-run" class="wiz-run"></code>
          <div id="wiz-example-box" style="display:none; margin-top:1rem;">
            <a id="wiz-example-link" class="wiz-example-link" href="#" target="_blank">
              <span id="wiz-example-label"></span>
              <span id="wiz-example-desc" style="display:block; font-size:0.75rem; color:var(--text-muted); font-weight:400;"></span>
            </a>
          </div>
          <div class="wiz-card-title">What You'll Learn</div>
          <ul id="wiz-learn" class="wiz-learn-list"></ul>
        </div>
        <div class="wiz-card wiz-card-full">
          <div class="wiz-card-title">Tools &amp; Services by Category</div>
          <div id="wiz-apps"></div>
        </div>
        <div class="wiz-card wiz-card-full">
          <div class="wiz-card-title">Starter Code <button class="copy-btn" onclick="copyCode()">Copy</button></div>
          <pre id="wiz-code" class="wiz-code"><code id="wiz-code-inner" class="language-python"></code></pre>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="stats-grid">
  <div class="stat-card"><div class="stat-number">{total_workflows:,}</div><div class="stat-label">Workflows Analyzed</div></div>
  <div class="stat-card"><div class="stat-number">{total_patterns:,}</div><div class="stat-label">Unique Patterns Found</div></div>
  <div class="stat-card"><div class="stat-number">12</div><div class="stat-label">Use Case Categories</div></div>
</div>

<!-- PATTERNS -->
<section id="patterns">
  <h2>Most Common Patterns</h2>
  <p class="section-desc">
    A "pattern" is the sequence of abstract steps a workflow follows, like
    <span class="step step-trigger">trigger</span> &rarr;
    <span class="step step-ai">ai</span> &rarr;
    <span class="step step-deliver">deliver</span>.
    The specific tool doesn't matter &mdash; what matters is the structure.
    These are the 10 most frequent patterns across all {total_workflows:,} workflows.
  </p>
  <div class="chart-container" style="margin-bottom:1.5rem;">
    <canvas id="patChart"></canvas>
  </div>
  {pattern_cards}
</section>

<!-- BUILDING BLOCKS -->
<section id="building-blocks">
  <h2>Most-Used Tools</h2>
  <p class="section-desc">
    The concrete tools and services that appear most often across all workflows.
    Each tool belongs to a category like
    <span class="step step-ai">ai</span>,
    <span class="step step-trigger">trigger</span>, or
    <span class="step step-deliver">deliver</span> &mdash;
    together they form the building blocks of any automation.
  </p>
  <table>
    <thead><tr><th>Tool</th><th>Category</th><th>What it does</th><th>Usage</th></tr></thead>
    <tbody>{blocks_html}</tbody>
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
// --- Pattern chart ---
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

// --- Wizard ---
const wizardData = {wizard_json};

function renderSteps(pattern) {{
  return pattern.split(' -> ').map(s => {{
    return `<span class="step step-${{s}}">${{s}}</span>`;
  }}).join(' &#8594; ');
}}

// Build wizard cards
const cardsEl = document.getElementById('wizard-cards');
wizardData.forEach((uc, i) => {{
  const card = document.createElement('div');
  card.className = 'wizard-card';
  card.onclick = () => wizardSelect(i);
  card.innerHTML = `
    <div class="wizard-card-icon">${{uc.icon}}</div>
    <h4>${{uc.name}}</h4>
    <p>"${{uc.question}}"</p>
    <div class="wizard-card-count">${{uc.count.toLocaleString()}} workflows (${{uc.pct.toFixed(0)}}%)</div>
  `;
  cardsEl.appendChild(card);
}});

function wizardSelect(index) {{
  const uc = wizardData[index];
  document.getElementById('wiz-icon').textContent = uc.icon;
  document.getElementById('wiz-name').textContent = uc.name;
  document.getElementById('wiz-stats').textContent =
    `${{uc.count.toLocaleString()}} real workflows · avg. ${{uc.avg_nodes.toFixed(0)}} nodes`;
  document.getElementById('wiz-desc').textContent = uc.desc;
  document.getElementById('wiz-pattern').innerHTML = renderSteps(uc.pattern);
  document.getElementById('wiz-claude').textContent = uc.claude_code;
  document.getElementById('wiz-run').textContent = uc.run;
  const codeEl = document.getElementById('wiz-code-inner');
  codeEl.textContent = uc.code;
  if (window.Prism) Prism.highlightElement(codeEl);

  const toolsEl = document.getElementById('wiz-tools');
  toolsEl.innerHTML = uc.tools.map(t => `<li>${{t}}</li>`).join('');

  // Group apps by category
  const groups = {{}};
  const catOrder = ['ai','data','deliver','storage','api','trigger','transform','logic'];
  uc.apps.forEach(a => {{
    if (!groups[a.cat]) groups[a.cat] = [];
    groups[a.cat].push(a);
  }});
  const appsEl = document.getElementById('wiz-apps');
  appsEl.innerHTML = catOrder
    .filter(cat => groups[cat])
    .map(cat => `<div class="wiz-app-group">
      <span class="wiz-app-group-label"><span class="step step-${{cat}}">${{cat}}</span></span>
      <div class="wiz-app-group-items">
        ${{groups[cat].map(a => `<span class="wiz-app-item">${{a.name}} <span class="wiz-app-count">${{a.count.toLocaleString()}}x</span></span>`).join('')}}
      </div>
    </div>`).join('');

  // Example link
  const exBox = document.getElementById('wiz-example-box');
  if (uc.example) {{
    document.getElementById('wiz-example-link').href =
      `https://github.com/janrummel/workflow-patterns/tree/main/${{uc.example.path}}`;
    document.getElementById('wiz-example-label').textContent = uc.example.label;
    document.getElementById('wiz-example-desc').textContent = uc.example.desc;
    exBox.style.display = 'block';
  }} else {{
    exBox.style.display = 'none';
  }}

  const learnEl = document.getElementById('wiz-learn');
  learnEl.innerHTML = uc.learn.map(l => `<li>${{l}}</li>`).join('');

  document.getElementById('wizard-step1').style.display = 'none';
  document.getElementById('wizard-step2').style.display = 'block';
  document.getElementById('wizard').scrollIntoView({{ behavior:'smooth' }});
}}

function wizardBack() {{
  document.getElementById('wizard-step1').style.display = 'block';
  document.getElementById('wizard-step2').style.display = 'none';
  document.getElementById('wizard').scrollIntoView({{ behavior:'smooth' }});
}}

function copyCode() {{
  const code = document.getElementById('wiz-code-inner').textContent;
  navigator.clipboard.writeText(code).then(() => {{
    const btn = document.querySelector('.copy-btn');
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 1500);
  }});
}}
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()
