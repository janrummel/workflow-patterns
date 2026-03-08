# Email Automation Example — Design

**Date:** 2026-03-08
**Pattern:** `trigger → transform → deliver`
**Status:** Approved

## Goal

Third runnable example for workflow-patterns. A template-based email automation system that renders personalized emails from presets and delivers them as HTML files (default) or via SMTP (optional). Demonstrates the simplest workflow pattern without AI dependency.

## Architecture

```
select_template() → render_email() → save_or_send()
trigger              transform         deliver
```

## Module Structure

```
examples/email-automation/
├── run.py                      # CLI entry point
├── .env.example                # SMTP config template (optional)
├── .gitignore                  # .env, __pycache__, output/
├── pyproject.toml              # no runtime dependencies
├── src/email_workflow/
│   ├── __init__.py
│   ├── models.py               # Dataclasses: Template, Recipient, Email
│   ├── templates.py            # 5 email template presets
│   ├── renderer.py             # Template rendering (variable substitution, HTML)
│   ├── sender.py               # File output (default) + SMTP delivery (--send)
│   └── display.py              # Terminal formatting
├── tests/
│   ├── test_models.py
│   ├── test_templates.py
│   ├── test_renderer.py
│   ├── test_sender.py
│   └── test_display.py
└── output/                     # Rendered emails (gitignored)
```

## Modules

### models.py
```python
@dataclass
class Template:
    name: str
    subject: str
    body: str           # with {variable} placeholders
    variables: list[str]  # required variable names

@dataclass
class Recipient:
    name: str
    email: str

@dataclass
class Email:
    recipient: Recipient
    subject: str
    body_html: str
    body_text: str
```

### templates.py
5 curated email templates:

| Template | Variables | Use Case |
|----------|-----------|----------|
| Order Confirmation | name, order_id, items, total | E-Commerce |
| Welcome Email | name, product | Onboarding |
| Invoice Reminder | name, amount, due_date | Billing |
| Event Invitation | name, event, date, location | Events |
| Password Reset | name, reset_link | Security |

Interactive selection menu (same UX as chatbot personas). Also available via `--template` flag.

### renderer.py
- `render_email(template, recipient, variables)` → `Email`
- Substitutes `{variable}` placeholders with provided values
- Generates both HTML (with basic styling) and plain text versions
- Validates all required variables are provided

### sender.py
- `save_email(email, directory)` → saves as `.html` file (default mode)
- `send_email(email, smtp_config)` → sends via SMTP (with `--send` flag)
- SMTP config from `.env`: host, port, username, password

### display.py
- `format_header(title)` — boxed header (same style as chatbot)
- `format_template_menu(templates)` — template selection list
- `format_preview(email)` — show rendered email before saving/sending

## UX Flow

```
$ uv run python run.py

╔══════════════════════════════════════════╗
║       Email Automation — Setup          ║
╚══════════════════════════════════════════╝

Choose a template:

  1. Order Confirmation      E-Commerce order receipt
  2. Welcome Email           New user onboarding
  3. Invoice Reminder        Payment due notification
  4. Event Invitation        Event RSVP
  5. Password Reset          Security reset link

Template (1-5): 2

── Welcome Email ──

Recipient name: Jan
Recipient email: jan@example.com
product: Workflow Patterns Pro

Preview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject: Welcome to Workflow Patterns Pro!
To: Jan <jan@example.com>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hi Jan,

Welcome to Workflow Patterns Pro! We're excited ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Email saved to output/2026-03-08_welcome-email_jan.html
```

## Key Differences from Other Examples

| Aspect | Content Creation | Chatbot | Email Automation |
|--------|-----------------|---------|-----------------|
| API style | `messages.create()` | `messages.stream()` | No AI — pure templates |
| Interaction | One-shot | Interactive loop | One-shot with preview |
| Pattern | `api → ai → transform → deliver` | `trigger → ai → data → deliver` | `trigger → transform → deliver` |
| Dependencies | anthropic | anthropic | None (stdlib only) |
| Output | Markdown file | Terminal + JSON | HTML file or SMTP |

## Dependencies

- No runtime dependencies (stdlib only: `smtplib`, `email`, `string`)
- `pytest` (dev)

## Testing Strategy

- Dataclass tests for models
- Template validation tests (all variables present, unique names)
- Renderer tests (variable substitution, HTML generation, missing variable handling)
- Sender tests (file output with tmp_path, SMTP mocking)
- Display formatting tests
- Target: ~20-25 tests
