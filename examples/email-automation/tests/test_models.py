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
