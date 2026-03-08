"""Tests for api_workflow.display."""

from api_workflow.display import format_header, format_integration_menu, format_records_table
from api_workflow.models import ApiConfig, Integration, TransformSpec


class TestFormatHeader:
    def test_contains_title(self):
        assert "Test" in format_header("Test")

    def test_has_box_chars(self):
        assert "═" in format_header("Test")


class TestFormatIntegrationMenu:
    def test_lists_all(self):
        integrations = [
            Integration(
                name="A", description="D1",
                api=ApiConfig(base_url="", endpoint=""),
                transform=TransformSpec(extract_path="", fields=[]),
            ),
            Integration(
                name="B", description="D2",
                api=ApiConfig(base_url="", endpoint=""),
                transform=TransformSpec(extract_path="", fields=[]),
            ),
        ]
        result = format_integration_menu(integrations)
        assert "1." in result
        assert "2." in result


class TestFormatRecordsTable:
    def test_formats_records(self):
        records = [{"name": "Alice", "score": "95"}]
        table = format_records_table(records)
        assert "Alice" in table
        assert "name" in table

    def test_empty_records(self):
        table = format_records_table([])
        assert "no" in table.lower() or "empty" in table.lower()
