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
