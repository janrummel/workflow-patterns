"""Tests for api_workflow.transform."""

from api_workflow.models import TransformSpec
from api_workflow.transform import extract_path, pick_fields, transform_response


class TestExtractPath:
    def test_simple_path(self):
        data = {"items": [1, 2, 3]}
        assert extract_path(data, "items") == [1, 2, 3]

    def test_nested_path(self):
        data = {"data": {"results": [{"id": 1}]}}
        assert extract_path(data, "data.results") == [{"id": 1}]

    def test_empty_path_returns_data(self):
        data = [{"id": 1}]
        assert extract_path(data, "") == [{"id": 1}]

    def test_missing_path_returns_empty(self):
        data = {"other": "value"}
        assert extract_path(data, "missing.path") == []

    def test_single_object_wrapped_in_list(self):
        data = {"item": {"id": 1}}
        result = extract_path(data, "item")
        assert result == [{"id": 1}]


class TestPickFields:
    def test_pick_specified_fields(self):
        records = [{"id": 1, "name": "A", "extra": "x"}]
        result = pick_fields(records, ["id", "name"])
        assert result == [{"id": 1, "name": "A"}]

    def test_missing_field_uses_empty(self):
        records = [{"id": 1}]
        result = pick_fields(records, ["id", "missing"])
        assert result == [{"id": 1, "missing": ""}]

    def test_empty_fields_returns_all(self):
        records = [{"a": 1, "b": 2}]
        result = pick_fields(records, [])
        assert result == [{"a": 1, "b": 2}]


class TestTransformResponse:
    def test_full_transform(self):
        data = {"data": {"repos": [
            {"name": "repo1", "stars": 100, "lang": "Python"},
            {"name": "repo2", "stars": 50, "lang": "Go"},
        ]}}
        spec = TransformSpec(extract_path="data.repos", fields=["name", "stars"])
        result = transform_response(data, spec)
        assert len(result) == 2
        assert result[0] == {"name": "repo1", "stars": 100}

    def test_transform_empty_data(self):
        spec = TransformSpec(extract_path="items", fields=["id"])
        result = transform_response({"items": []}, spec)
        assert result == []

    def test_transform_with_rename(self):
        data = {"items": [{"old_name": "val"}]}
        spec = TransformSpec(
            extract_path="items",
            fields=["old_name"],
            rename={"old_name": "new_name"},
        )
        result = transform_response(data, spec)
        assert result[0]["new_name"] == "val"
