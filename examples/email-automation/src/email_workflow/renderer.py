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
    body_html_content = "".join(
        f"<p>{p.replace(chr(10), '<br>')}</p>" for p in body_paragraphs
    )

    body_html = HTML_TEMPLATE.format(subject=subject, body_html=body_html_content)

    return Email(
        recipient=recipient,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        template_name=template.name,
    )
