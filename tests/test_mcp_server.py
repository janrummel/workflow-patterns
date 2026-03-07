"""Tests for the MCP server tools."""

from workflow_patterns.mcp_server.server import (
    list_categories,
    search_patterns,
    show_all_patterns,
    suggest_implementation,
)


def test_search_patterns_returns_results():
    result = search_patterns("Send a weekly AI summary by email")
    assert "Detected categories" in result
    assert "trigger" in result
    assert "ai" in result


def test_search_patterns_with_data_keywords():
    result = search_patterns("Fetch data from a spreadsheet and analyze it")
    assert "data" in result


def test_suggest_implementation_returns_architecture():
    result = suggest_implementation("trigger -> ai -> deliver")
    assert "Components needed" in result
    assert "Implementation steps" in result
    assert "Claude Agent" in result


def test_list_categories_shows_stats():
    result = list_categories()
    assert "workflows analyzed" in result
    assert "ai" in result
    assert "trigger" in result


def test_show_all_patterns_returns_patterns():
    result = show_all_patterns()
    assert "unique patterns" in result
    assert "->" in result
