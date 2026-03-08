"""Tests for persona presets."""

from chatbot.models import Persona
from chatbot.personas import PERSONAS, get_persona


def test_has_five_personas():
    assert len(PERSONAS) == 5


def test_all_personas_are_persona_instances():
    for p in PERSONAS:
        assert isinstance(p, Persona)


def test_all_personas_have_system_prompts():
    for p in PERSONAS:
        assert len(p.system_prompt) > 50, f"{p.name} system prompt too short"


def test_all_personas_have_unique_names():
    names = [p.name for p in PERSONAS]
    assert len(names) == len(set(names))


def test_get_persona_by_index():
    p = get_persona(0)
    assert p == PERSONAS[0]


def test_get_persona_out_of_range_returns_first():
    p = get_persona(99)
    assert p == PERSONAS[0]
