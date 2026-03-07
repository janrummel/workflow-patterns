"""Tests for the Claude Code translator."""

from workflow_patterns.translator.claude_code import translate_pattern


def test_simple_pattern():
    arch = translate_pattern("trigger -> ai -> deliver")
    assert arch.complexity == "medium"  # 3 categories = medium
    assert len(arch.components) == 3
    assert arch.summary
    assert len(arch.implementation_steps) > 0


def test_medium_pattern():
    arch = translate_pattern("trigger -> ai -> transform -> deliver")
    assert arch.complexity == "medium"
    assert len(arch.components) == 4


def test_complex_pattern():
    arch = translate_pattern("trigger -> ai -> data -> transform -> api -> deliver")
    assert arch.complexity == "high"
    assert len(arch.components) == 6


def test_to_text_contains_pattern():
    arch = translate_pattern("trigger -> ai -> deliver")
    text = arch.to_text()
    assert "trigger -> ai -> deliver" in text
    assert "Components needed" in text
    assert "Implementation steps" in text


def test_components_have_mcp_servers():
    arch = translate_pattern("trigger -> data -> deliver")
    types = [c.component_type for c in arch.components]
    assert "mcp_server" in types  # data and deliver both need MCP servers


def test_unknown_category_handled():
    arch = translate_pattern("trigger -> unknown_thing -> deliver")
    # Should not crash, just skip unknown categories
    assert arch.summary
    assert len(arch.components) >= 2  # at least trigger and deliver
