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


def _collect_recipient() -> Recipient:
    """Interactively collect recipient info."""
    try:
        name = input("Recipient name: ").strip() or "Recipient"
        email = input("Recipient email: ").strip() or "recipient@example.com"
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(0)
    return Recipient(name=name, email=email)


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
