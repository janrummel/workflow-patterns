"""Tests for pipeline.display."""

from pipeline.display import format_header, format_pipeline_menu, format_stats
from pipeline.models import Dataset, Pipeline, Record, TransformStep


class TestFormatHeader:
    def test_contains_title(self):
        assert "Pipeline" in format_header("Pipeline")

    def test_has_box_chars(self):
        assert "═" in format_header("Test")


class TestFormatPipelineMenu:
    def test_lists_all(self):
        pipes = [
            Pipeline(name="A", description="Desc A", steps=[]),
            Pipeline(name="B", description="Desc B", steps=[]),
        ]
        result = format_pipeline_menu(pipes)
        assert "1." in result
        assert "2." in result
        assert "A" in result


class TestFormatStats:
    def test_shows_counts(self):
        ds = Dataset(
            headers=["a", "b"],
            records=[Record(data={"a": "1", "b": "2"})],
        )
        result = format_stats(ds)
        assert "1" in result
        assert "2" in result
