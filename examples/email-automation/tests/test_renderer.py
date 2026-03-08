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


def test_render_html_converts_newlines():
    t = Template(name="T", subject="S", body="Line 1\nLine 2\n\nLine 3", variables=[])
    r = Recipient(name="Jan", email="jan@example.com")
    email = render_email(t, r, {})
    assert "<br>" in email.body_html or "<p>" in email.body_html
