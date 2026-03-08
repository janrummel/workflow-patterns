"""Terminal display formatting for the chatbot."""

from chatbot.models import Persona


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


def format_persona_menu(personas: list[Persona]) -> str:
    """Format the persona selection menu."""
    lines = ["Choose a persona:", ""]
    for i, p in enumerate(personas, 1):
        lines.append(f"  {i}. {p.name:<25} {p.description}")
    lines.append("")
    return "\n".join(lines)


def format_welcome(persona: Persona) -> str:
    """Format the welcome message after persona selection."""
    lines = [
        "",
        f"── {persona.name} ──",
        "Type your message. Commands: /save, /load, /quit",
        "",
    ]
    return "\n".join(lines)
