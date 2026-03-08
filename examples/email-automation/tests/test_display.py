"""Tests for terminal display formatting."""

from email_workflow.display import format_header, format_preview, format_template_menu
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
