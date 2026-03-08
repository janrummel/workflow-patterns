"""Tests for terminal display formatting."""

from chatbot.display import format_header, format_persona_menu, format_welcome
from chatbot.models import Persona


def test_format_header():
    result = format_header("AI Chatbot")
    assert "AI Chatbot" in result
    assert "╔" in result


def test_format_persona_menu():
    personas = [
        Persona(name="Coder", description="Writes code", system_prompt="S"),
        Persona(name="Writer", description="Writes text", system_prompt="S"),
    ]
    result = format_persona_menu(personas)
    assert "1." in result
    assert "2." in result
    assert "Coder" in result
    assert "Writes text" in result


def test_format_welcome():
    persona = Persona(name="Research Assistant", description="D", system_prompt="S")
    result = format_welcome(persona)
    assert "Research Assistant" in result
    assert "/quit" in result
