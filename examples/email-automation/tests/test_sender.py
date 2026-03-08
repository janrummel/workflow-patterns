"""Tests for email delivery (file output and SMTP)."""

from email_workflow.models import Email, Recipient
from email_workflow.sender import build_mime_message, save_email


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
