"""Tests for pipeline.reader."""

import json

from pipeline.models import Dataset
from pipeline.reader import (
    from_dicts,
    generate_sample_data,
    read_csv,
    read_json,
)


class TestFromDicts:
    def test_basic(self):
        ds = from_dicts(
            headers=["a", "b"],
            rows=[{"a": "1", "b": "2"}, {"a": "3", "b": "4"}],
        )
        assert ds.row_count == 2
        assert ds.headers == ["a", "b"]

    def test_empty(self):
        ds = from_dicts(headers=["x"], rows=[])
        assert ds.row_count == 0


class TestReadCsv:
    def test_read_csv_file(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,value\nAlice,100\nBob,200\n")
        ds = read_csv(csv_file)
        assert ds.headers == ["name", "value"]
        assert ds.row_count == 2
        assert ds.records[0].data["name"] == "Alice"

    def test_read_csv_missing_file(self, tmp_path):
        ds = read_csv(tmp_path / "missing.csv")
        assert ds.row_count == 0

    def test_read_csv_empty_file(self, tmp_path):
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")
        ds = read_csv(csv_file)
        assert ds.row_count == 0


class TestReadJson:
    def test_read_json_file(self, tmp_path):
        data = [{"name": "Alice", "value": "100"}, {"name": "Bob", "value": "200"}]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data))
        ds = read_json(json_file)
        assert ds.row_count == 2
        assert "name" in ds.headers

    def test_read_json_missing_file(self, tmp_path):
        ds = read_json(tmp_path / "missing.json")
        assert ds.row_count == 0


class TestGenerateSampleData:
    def test_generates_records(self):
        ds = generate_sample_data()
        assert ds.row_count >= 20

    def test_has_expected_columns(self):
        ds = generate_sample_data()
        for col in ["date", "region", "product", "units", "revenue"]:
            assert col in ds.headers

    def test_all_records_have_data(self):
        ds = generate_sample_data()
        for rec in ds.records:
            assert rec.data.get("product")
            assert rec.data.get("revenue")
