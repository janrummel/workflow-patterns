"""Tests for pipeline.writer."""

from pipeline.models import Dataset, Record
from pipeline.writer import to_table_string, write_csv, write_json


def _ds(rows, headers=None):
    if headers is None:
        headers = list(rows[0].keys()) if rows else []
    return Dataset(headers=headers, records=[Record(data=r) for r in rows])


class TestWriteCsv:
    def test_write_and_read_back(self, tmp_path):
        ds = _ds([{"a": "1", "b": "2"}, {"a": "3", "b": "4"}])
        path = write_csv(ds, tmp_path / "out.csv")
        assert path.exists()
        lines = path.read_text().strip().split("\n")
        assert lines[0] == "a,b"
        assert len(lines) == 3

    def test_creates_parent_dirs(self, tmp_path):
        ds = _ds([{"x": "1"}])
        path = write_csv(ds, tmp_path / "sub" / "out.csv")
        assert path.exists()


class TestWriteJson:
    def test_write_json(self, tmp_path):
        ds = _ds([{"name": "Alice"}, {"name": "Bob"}])
        path = write_json(ds, tmp_path / "out.json")
        assert path.exists()
        import json
        data = json.loads(path.read_text())
        assert len(data) == 2


class TestToTableString:
    def test_basic_table(self):
        ds = _ds([{"name": "Alice", "age": "30"}])
        table = to_table_string(ds)
        assert "name" in table
        assert "Alice" in table

    def test_max_rows(self):
        ds = _ds([{"v": str(i)} for i in range(20)])
        table = to_table_string(ds, max_rows=5)
        assert "..." in table or "more" in table.lower()

    def test_empty_dataset(self):
        ds = _ds([], headers=["a"])
        table = to_table_string(ds)
        assert "empty" in table.lower() or "no" in table.lower() or table.strip()
