"""Email delivery: save to file or send via SMTP."""

import smtplib
import ssl
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

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
