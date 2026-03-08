"""Tests for api_workflow.storage."""

import json

from api_workflow.storage import save_csv, save_json


class TestSaveJson:
    def test_saves_records(self, tmp_path):
        records = [{"name": "A", "value": "1"}]
        path = save_json(records, tmp_path, "test")
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data) == 1

    def test_creates_dir(self, tmp_path):
        path = save_json([{"x": 1}], tmp_path / "sub", "test")
        assert path.exists()


class TestSaveCsv:
    def test_saves_records(self, tmp_path):
        records = [{"name": "A", "value": "1"}, {"name": "B", "value": "2"}]
        path = save_csv(records, tmp_path, "test")
        assert path.exists()
        lines = path.read_text().strip().split("\n")
        assert len(lines) == 3  # header + 2 rows

    def test_empty_records(self, tmp_path):
        path = save_csv([], tmp_path, "test")
        assert path.exists()
