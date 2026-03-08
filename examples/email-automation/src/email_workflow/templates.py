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
