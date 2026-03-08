# Email Automation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a template-based email automation system with 5 presets, HTML rendering, and optional SMTP delivery as the third runnable example.

**Architecture:** CLI selects a template, collects variables interactively, renders HTML + plain text, and saves to file (default) or sends via SMTP (`--send`). Pattern: `trigger → transform → deliver`. No AI dependency — pure stdlib.

**Tech Stack:** Python 3.12+, stdlib only (`string.Template`, `smtplib`, `email`), `pytest`, `uv`

---

### Task 1: Project scaffolding

**Files:**
- Create: `examples/email-automation/pyproject.toml`
- Create: `examples/email-automation/.env.example`
- Create: `examples/email-automation/.gitignore`
- Create: `examples/email-automation/src/email_workflow/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "email-automation"
version = "0.1.0"
description = "Email Automation workflow: trigger -> transform -> deliver"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["pytest"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/email_workflow"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: Create .env.example**

```
# Optional: only needed if you use --send to deliver via SMTP
# cp .env.example .env
#
# .env is in .gitignore — it will never be committed.
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
```

**Step 3: Create .gitignore**

```
.venv/
output/
__pycache__/
*.egg-info/
.env
```

**Step 4: Create empty `src/email_workflow/__init__.py`**

**Step 5: Run `uv sync` to verify project setup**

Run: `cd examples/email-automation && uv sync`
Expected: Resolves and installs dev dependencies

**Step 6: Commit**

```bash
git add examples/email-automation/
git commit -m "Scaffold Email Automation example project"
```

---

### Task 2: Data models

**Files:**
- Create: `examples/email-automation/tests/test_models.py`
- Create: `examples/email-automation/src/email_workflow/models.py`

**Step 1: Write failing tests**

```python
"""Tests for email workflow data models."""

from email_workflow.models import Email, Recipient, Template


def test_template_has_required_fields():
    t = Template(
        name="Test",
        subject="Hello {name}",
        body="Hi {name}, welcome to {product}.",
        variables=["name", "product"],
    )
    assert t.name == "Test"
    assert t.variables == ["name", "product"]


def test_template_description():
    t = Template(
        name="Test",
        subject="S",
        body="B",
        variables=[],
        description="A test template",
    )
    assert t.description == "A test template"


def test_recipient_has_name_and_email():
    r = Recipient(name="Jan", email="jan@example.com")
    assert r.name == "Jan"
    assert r.email == "jan@example.com"


def test_email_has_all_fields():
    r = Recipient(name="Jan", email="jan@example.com")
    e = Email(
        recipient=r,
        subject="Welcome",
        body_html="<p>Hi Jan</p>",
        body_text="Hi Jan",
        template_name="Welcome Email",
    )
    assert e.recipient.email == "jan@example.com"
    assert e.subject == "Welcome"
    assert "<p>" in e.body_html
    assert e.template_name == "Welcome Email"
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/email-automation && uv run pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'email_workflow.models'`

**Step 3: Write implementation**

```python
"""Data models for the email workflow."""

from dataclasses import dataclass, field


@dataclass
class Template:
    """An email template with variable placeholders."""

    name: str
    subject: str
    body: str
    variables: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class Recipient:
    """An email recipient."""

    name: str
    email: str


@dataclass
class Email:
    """A rendered email ready for delivery."""

    recipient: Recipient
    subject: str
    body_html: str
    body_text: str
    template_name: str = ""
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/email-automation && uv run pytest tests/test_models.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add examples/email-automation/src/email_workflow/models.py examples/email-automation/tests/test_models.py
git commit -m "Add email workflow data models with tests"
```

---

### Task 3: Email templates

**Files:**
- Create: `examples/email-automation/tests/test_templates.py`
- Create: `examples/email-automation/src/email_workflow/templates.py`

**Step 1: Write failing tests**

```python
"""Tests for email template presets."""

from email_workflow.models import Template
from email_workflow.templates import TEMPLATES, get_template


def test_has_five_templates():
    assert len(TEMPLATES) == 5


def test_all_templates_are_template_instances():
    for t in TEMPLATES:
        assert isinstance(t, Template)


def test_all_templates_have_variables():
    for t in TEMPLATES:
        assert len(t.variables) > 0, f"{t.name} has no variables"


def test_all_templates_have_unique_names():
    names = [t.name for t in TEMPLATES]
    assert len(names) == len(set(names))


def test_all_templates_have_placeholders_matching_variables():
    for t in TEMPLATES:
        for var in t.variables:
            assert f"{{{var}}}" in t.body or f"{{{var}}}" in t.subject, (
                f"{t.name}: variable '{var}' not found in body or subject"
            )


def test_get_template_by_index():
    t = get_template(0)
    assert t == TEMPLATES[0]


def test_get_template_out_of_range_returns_first():
    t = get_template(99)
    assert t == TEMPLATES[0]
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/email-automation && uv run pytest tests/test_templates.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
"""Email template presets."""

from email_workflow.models import Template

TEMPLATES = [
    Template(
        name="Order Confirmation",
        description="E-Commerce order receipt",
        subject="Order #{order_id} confirmed",
        body=(
            "Hi {name},\n\n"
            "Thank you for your order #{order_id}!\n\n"
            "Items: {items}\n"
            "Total: {total}\n\n"
            "We'll notify you when your order ships.\n\n"
            "Best regards,\nThe Team"
        ),
        variables=["name", "order_id", "items", "total"],
    ),
    Template(
        name="Welcome Email",
        description="New user onboarding",
        subject="Welcome to {product}!",
        body=(
            "Hi {name},\n\n"
            "Welcome to {product}! We're excited to have you on board.\n\n"
            "Here's what you can do next:\n"
            "1. Complete your profile\n"
            "2. Explore the dashboard\n"
            "3. Check out our getting started guide\n\n"
            "If you have any questions, just reply to this email.\n\n"
            "Cheers,\nThe {product} Team"
        ),
        variables=["name", "product"],
    ),
    Template(
        name="Invoice Reminder",
        description="Payment due notification",
        subject="Reminder: Invoice due {due_date}",
        body=(
            "Hi {name},\n\n"
            "This is a friendly reminder that your invoice for {amount} "
            "is due on {due_date}.\n\n"
            "If you've already paid, please disregard this message.\n\n"
            "Best regards,\nAccounting Team"
        ),
        variables=["name", "amount", "due_date"],
    ),
    Template(
        name="Event Invitation",
        description="Event RSVP",
        subject="You're invited: {event}",
        body=(
            "Hi {name},\n\n"
            "You're invited to {event}!\n\n"
            "Date: {date}\n"
            "Location: {location}\n\n"
            "We'd love to see you there. Please RSVP by replying to this email.\n\n"
            "Looking forward to it,\nThe Events Team"
        ),
        variables=["name", "event", "date", "location"],
    ),
    Template(
        name="Password Reset",
        description="Security reset link",
        subject="Reset your password",
        body=(
            "Hi {name},\n\n"
            "We received a request to reset your password.\n\n"
            "Click here to reset: {reset_link}\n\n"
            "If you didn't request this, you can safely ignore this email. "
            "The link expires in 24 hours.\n\n"
            "Security Team"
        ),
        variables=["name", "reset_link"],
    ),
]


def get_template(index: int) -> Template:
    """Get a template by index, defaulting to first if out of range."""
    if 0 <= index < len(TEMPLATES):
        return TEMPLATES[index]
    return TEMPLATES[0]
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/email-automation && uv run pytest tests/test_templates.py -v`
Expected: 7 passed

**Step 5: Commit**

```bash
git add examples/email-automation/src/email_workflow/templates.py examples/email-automation/tests/test_templates.py
git commit -m "Add 5 email template presets with tests"
```

---

### Task 4: Template renderer

**Files:**
- Create: `examples/email-automation/tests/test_renderer.py`
- Create: `examples/email-automation/src/email_workflow/renderer.py`

**Step 1: Write failing tests**

```python
"""Tests for email template renderer."""

import pytest

from email_workflow.models import Recipient, Template
from email_workflow.renderer import render_email


def _make_template() -> Template:
    return Template(
        name="Test",
        subject="Hello {name}",
        body="Hi {name}, welcome to {product}.",
        variables=["name", "product"],
    )


def test_render_substitutes_variables():
    t = _make_template()
    r = Recipient(name="Jan", email="jan@example.com")
    email = render_email(t, r, {"name": "Jan", "product": "Acme"})
    assert email.subject == "Hello Jan"
    assert "welcome to Acme" in email.body_text


def test_render_produces_html():
    t = _make_template()
    r = Recipient(name="Jan", email="jan@example.com")
    email = render_email(t, r, {"name": "Jan", "product": "Acme"})
    assert "<html>" in email.body_html.lower()
    assert "welcome to Acme" in email.body_html


def test_render_sets_recipient():
    t = _make_template()
    r = Recipient(name="Jan", email="jan@example.com")
    email = render_email(t, r, {"name": "Jan", "product": "Acme"})
    assert email.recipient.email == "jan@example.com"


def test_render_sets_template_name():
    t = _make_template()
    r = Recipient(name="Jan", email="jan@example.com")
    email = render_email(t, r, {"name": "Jan", "product": "Acme"})
    assert email.template_name == "Test"


def test_render_missing_variable_raises():
    t = _make_template()
    r = Recipient(name="Jan", email="jan@example.com")
    with pytest.raises(ValueError, match="Missing variables"):
        render_email(t, r, {"name": "Jan"})  # missing 'product'


def test_render_html_escapes_newlines():
    t = Template(name="T", subject="S", body="Line 1\nLine 2\n\nLine 3", variables=[])
    r = Recipient(name="Jan", email="jan@example.com")
    email = render_email(t, r, {})
    assert "<br>" in email.body_html or "<p>" in email.body_html
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/email-automation && uv run pytest tests/test_renderer.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
"""Template renderer: substitutes variables and generates HTML."""

from email_workflow.models import Email, Recipient, Template

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }}
        .footer {{ border-top: 1px solid #eee; padding-top: 10px; margin-top: 20px; font-size: 0.85em; color: #888; }}
    </style>
</head>
<body>
    <div class="header"><strong>{subject}</strong></div>
    <div class="content">{body_html}</div>
    <div class="footer">Sent by Email Automation — workflow-patterns</div>
</body>
</html>"""


def render_email(
    template: Template,
    recipient: Recipient,
    variables: dict[str, str],
) -> Email:
    """Render a template with variables into a ready-to-send Email.

    Raises ValueError if required variables are missing.
    """
    missing = [v for v in template.variables if v not in variables]
    if missing:
        raise ValueError(f"Missing variables: {', '.join(missing)}")

    subject = template.subject.format(**variables)
    body_text = template.body.format(**variables)

    body_paragraphs = body_text.split("\n\n")
    body_html_content = "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in body_paragraphs)

    body_html = HTML_TEMPLATE.format(subject=subject, body_html=body_html_content)

    return Email(
        recipient=recipient,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        template_name=template.name,
    )
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/email-automation && uv run pytest tests/test_renderer.py -v`
Expected: 6 passed

**Step 5: Commit**

```bash
git add examples/email-automation/src/email_workflow/renderer.py examples/email-automation/tests/test_renderer.py
git commit -m "Add template renderer with HTML generation"
```

---

### Task 5: Email delivery (file + SMTP)

**Files:**
- Create: `examples/email-automation/tests/test_sender.py`
- Create: `examples/email-automation/src/email_workflow/sender.py`

**Step 1: Write failing tests**

```python
"""Tests for email delivery (file output and SMTP)."""

from email_workflow.models import Email, Recipient
from email_workflow.sender import save_email, build_mime_message


def _make_email() -> Email:
    return Email(
        recipient=Recipient(name="Jan", email="jan@example.com"),
        subject="Test Subject",
        body_html="<html><body><p>Hello</p></body></html>",
        body_text="Hello",
        template_name="Welcome Email",
    )


def test_save_creates_html_file(tmp_path):
    email = _make_email()
    path = save_email(email, tmp_path)
    assert path.exists()
    assert path.suffix == ".html"


def test_save_file_contains_html(tmp_path):
    email = _make_email()
    path = save_email(email, tmp_path)
    content = path.read_text()
    assert "<html>" in content.lower()
    assert "Hello" in content


def test_save_filename_contains_template_and_recipient(tmp_path):
    email = _make_email()
    path = save_email(email, tmp_path)
    assert "welcome-email" in path.name
    assert "jan" in path.name


def test_build_mime_message_has_correct_headers():
    email = _make_email()
    msg = build_mime_message(email, "sender@example.com")
    assert msg["To"] == "jan@example.com"
    assert msg["Subject"] == "Test Subject"
    assert msg["From"] == "sender@example.com"


def test_build_mime_message_has_both_parts():
    email = _make_email()
    msg = build_mime_message(email, "sender@example.com")
    parts = list(msg.walk())
    content_types = [p.get_content_type() for p in parts]
    assert "text/plain" in content_types
    assert "text/html" in content_types
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/email-automation && uv run pytest tests/test_sender.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
"""Email delivery: save to file or send via SMTP."""

from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import smtplib
import ssl


from email_workflow.models import Email


def save_email(email: Email, directory: Path) -> Path:
    """Save a rendered email as an HTML file.

    Returns the path to the saved file.
    """
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    slug = email.template_name.lower().replace(" ", "-")
    recipient_slug = email.recipient.name.lower().replace(" ", "-")
    path = directory / f"{timestamp}_{slug}_{recipient_slug}.html"
    path.write_text(email.body_html)
    return path


def build_mime_message(email: Email, sender_email: str) -> MIMEMultipart:
    """Build a MIME message with both plain text and HTML parts."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = email.subject
    msg["From"] = sender_email
    msg["To"] = email.recipient.email

    msg.attach(MIMEText(email.body_text, "plain"))
    msg.attach(MIMEText(email.body_html, "html"))
    return msg


def send_email(email: Email, smtp_config: dict) -> None:
    """Send an email via SMTP.

    smtp_config keys: host, port, user, password, sender_email
    """
    msg = build_mime_message(email, smtp_config["sender_email"])
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        smtp_config["host"],
        int(smtp_config["port"]),
        context=context,
    ) as server:
        server.login(smtp_config["user"], smtp_config["password"])
        server.send_message(msg)
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/email-automation && uv run pytest tests/test_sender.py -v`
Expected: 5 passed

**Step 5: Commit**

```bash
git add examples/email-automation/src/email_workflow/sender.py examples/email-automation/tests/test_sender.py
git commit -m "Add email delivery: file output and SMTP"
```

---

### Task 6: Display formatting

**Files:**
- Create: `examples/email-automation/tests/test_display.py`
- Create: `examples/email-automation/src/email_workflow/display.py`

**Step 1: Write failing tests**

```python
"""Tests for terminal display formatting."""

from email_workflow.display import format_header, format_template_menu, format_preview
from email_workflow.models import Email, Recipient, Template


def test_format_header():
    result = format_header("Email Automation")
    assert "Email Automation" in result
    assert "╔" in result


def test_format_template_menu():
    templates = [
        Template(name="Welcome", description="Onboarding", subject="S", body="B", variables=[]),
        Template(name="Invoice", description="Billing", subject="S", body="B", variables=[]),
    ]
    result = format_template_menu(templates)
    assert "1." in result
    assert "2." in result
    assert "Welcome" in result
    assert "Billing" in result


def test_format_preview():
    email = Email(
        recipient=Recipient(name="Jan", email="jan@example.com"),
        subject="Welcome!",
        body_html="<p>Hi</p>",
        body_text="Hi Jan, welcome.",
        template_name="Welcome Email",
    )
    result = format_preview(email)
    assert "jan@example.com" in result
    assert "Welcome!" in result
    assert "Hi Jan" in result
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/email-automation && uv run pytest tests/test_display.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
"""Terminal display formatting for the email workflow."""

from email_workflow.models import Email, Template


def format_header(title: str) -> str:
    """Format a boxed header."""
    width = 42
    lines = [
        "",
        "╔" + "═" * width + "╗",
        "║" + title.center(width) + "║",
        "╚" + "═" * width + "╝",
        "",
    ]
    return "\n".join(lines)


def format_template_menu(templates: list[Template]) -> str:
    """Format the template selection menu."""
    lines = ["Choose a template:", ""]
    for i, t in enumerate(templates, 1):
        lines.append(f"  {i}. {t.name:<25} {t.description}")
    lines.append("")
    return "\n".join(lines)


def format_preview(email: Email) -> str:
    """Format an email preview for the terminal."""
    sep = "━" * 40
    lines = [
        "",
        "Preview:",
        sep,
        f"Subject: {email.subject}",
        f"To: {email.recipient.name} <{email.recipient.email}>",
        sep,
        email.body_text,
        sep,
        "",
    ]
    return "\n".join(lines)
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/email-automation && uv run pytest tests/test_display.py -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add examples/email-automation/src/email_workflow/display.py examples/email-automation/tests/test_display.py
git commit -m "Add terminal display formatting"
```

---

### Task 7: CLI runner (run.py)

**Files:**
- Create: `examples/email-automation/run.py`

**Step 1: Write run.py**

```python
#!/usr/bin/env python3
"""Email Automation workflow runner.

Pattern: trigger -> transform -> deliver

Template-based email automation with interactive variable input,
HTML rendering, and optional SMTP delivery.

Usage:
    uv run python run.py                  # interactive template selection
    uv run python run.py --template 2     # select template by number
    uv run python run.py --send           # send via SMTP instead of saving
"""

import argparse
import os
import sys
from pathlib import Path

from email_workflow.display import format_header, format_preview, format_template_menu
from email_workflow.models import Recipient
from email_workflow.renderer import render_email
from email_workflow.sender import save_email, send_email
from email_workflow.templates import TEMPLATES, get_template

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


def _select_template() -> int:
    """Interactive template selection. Returns 0-based index."""
    print(format_header("Email Automation — Setup"))
    print(format_template_menu(TEMPLATES))
    choice = input(f"Template (1-{len(TEMPLATES)}): ").strip()
    try:
        return int(choice) - 1
    except ValueError:
        return 0


def _collect_variables(template) -> dict[str, str]:
    """Interactively collect template variables."""
    print(f"\n── {template.name} ──\n")
    variables = {}
    for var in template.variables:
        try:
            value = input(f"  {var}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)
        variables[var] = value or f"[{var}]"
    return variables


def _collect_recipient() -> Recipient:
    """Interactively collect recipient info."""
    try:
        name = input("Recipient name: ").strip() or "Recipient"
        email = input("Recipient email: ").strip() or "recipient@example.com"
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(0)
    return Recipient(name=name, email=email)


def _get_smtp_config() -> dict:
    """Get SMTP config from environment variables."""
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SENDER_EMAIL"]
    config = {}
    for key in required:
        value = os.environ.get(key)
        if not value:
            print(f"Error: {key} not set. Check your .env file.")
            print("  cp .env.example .env  # then add your SMTP settings")
            sys.exit(1)
        config[key.lower().replace("smtp_", "")] = value
    config["sender_email"] = os.environ["SENDER_EMAIL"]
    return config


def main():
    _load_dotenv()

    parser = argparse.ArgumentParser(description="Email Automation: trigger -> transform -> deliver")
    parser.add_argument("--template", type=int, default=None, help="Template number (1-5)")
    parser.add_argument("--send", action="store_true", help="Send via SMTP instead of saving to file")
    args = parser.parse_args()

    # Step 1: Trigger — select template
    if args.template is not None:
        template = get_template(args.template - 1)
    else:
        template = get_template(_select_template())

    # Collect recipient and variables
    recipient = _collect_recipient()
    variables = _collect_variables(template)

    # Step 2: Transform — render email
    email = render_email(template, recipient, variables)
    print(format_preview(email))

    # Step 3: Deliver — save or send
    if args.send:
        smtp_config = _get_smtp_config()
        send_email(email, smtp_config)
        print(f"  Email sent to {email.recipient.email}")
    else:
        path = save_email(email, OUTPUT_DIR)
        print(f"  Email saved to {path}")


if __name__ == "__main__":
    main()
```

**Step 2: Verify all tests pass**

Run: `cd examples/email-automation && uv run pytest -v`
Expected: All tests pass (models: 4, templates: 7, renderer: 6, sender: 5, display: 3 = 25 total)

**Step 3: Commit**

```bash
git add examples/email-automation/run.py
git commit -m "Add CLI runner with interactive email workflow"
```

---

### Task 8: Integration — update README and website

**Files:**
- Modify: `README.md`
- Modify: `scripts/generate_site.py`

**Step 1: Update README.md**

In the "Runnable Examples" table, add the email-automation row:

```markdown
| [Email Automation](examples/email-automation/) | `trigger -> transform -> deliver` | Template-based emails with 5 presets, HTML rendering, and optional SMTP delivery |
```

Update "More examples coming" line to remove "Email Automation".

Update test count to reflect new total.

Update Project Structure to include `email-automation/`.

**Step 2: Update generate_site.py**

Add `example` field to the "Email Automation" entry in WIZARD_DATA:

```python
"example": {
    "path": "examples/email-automation",
    "label": "Runnable Example",
    "desc": "~25 tests, 5 templates, HTML rendering, optional SMTP — ready to run",
},
```

**Step 3: Regenerate site**

Run: `uv run python scripts/generate_site.py`

**Step 4: Run all tests**

Run: `uv run pytest -v` (from root)
Run: `cd examples/email-automation && uv run pytest -v`

**Step 5: Commit**

```bash
git add README.md scripts/generate_site.py docs/index.html
git commit -m "Link Email Automation example from README and website"
```

---

### Task 9: Live test and push

**Step 1: Test with piped input**

```bash
cd examples/email-automation && printf 'Jan\njan@example.com\nWorkflow Patterns Pro\n' | uv run python run.py --template 2
```

Verify: Welcome Email renders, HTML saved to output/.

**Step 2: Push**

```bash
git push
```
