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
